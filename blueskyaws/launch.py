import asyncio
import logging
import signal
import uuid

from afaws.config import Config as AwsConfig
from afaws.ec2.launch import Ec2Launcher
from afaws.ec2.initialization import InstanceInitializerSsh
from afaws.ec2.shutdown import AutoShutdownScheduler
#from afaws.ec2.execute import FailedToSshError, Ec2SshExecuter
from afaws.ec2.shutdown import Ec2Shutdown

from .config import substitude_config_wildcards

class AbortRun(RuntimeError):
    pass

class Ec2InstancesManager(object):

    def __init__(self, config, num_total, request_id, existing=None):
        self._config = config
        self._afaws_config = AwsConfig({
            "iam_instance_profile": self._config('aws', 'iam_instance_profile'),
            "default_efs_volumes": self._config('aws', 'ec2', 'efs_volumes')
        })
        self._num_total = num_total
        self._request_id = request_id
        self._existing_instances = existing
        self._new_instances = []
        self._launched = False

    async def __aenter__(self):
        self._set_signal_handlers()
        await self._launch()
        await self._schedule_auto_termination()
        await self._initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._terminate()
        self._reset_signal_handlers()

    SIGNAMES = ('SIGINT', 'SIGTERM')

    WAIT_FOR_LAUNCH_TIME = 5

    def _set_signal_handlers(self):
        self._old_signal_handlers = {
            s: signal.getsignal(getattr(signal, s)) for s in self.SIGNAMES
        }

        async def handler(signame):
            logging.warn("Receieved signal %s. Instances will be "
                "terminated and run will be aborted", signame)
            # If SIGINT or SIGTERM occur when any instances are still in the
            # 'pending' state, calling '_terminate' will miss them, since they
            # aren't added to self._new_instances until they're running.
            #
            # Options:
            #   1) update afaws package to split up launch into a) instance
            #     creation and b) waiting for running, so that instances are
            #     referenced immediatly after creation and can be terminated
            #     while in the 'pending' state.
            #   2) update handler to simply wait until launch has completed
            #     and returned.
            #
            # For now, at least, we're going with options 2)
            while not self._launched:
                logging.warn("Launch in progress. Waiting %s seconds before"
                    " terminating.", self.WAIT_FOR_LAUNCH_TIME)
                await asyncio.sleep(self.WAIT_FOR_LAUNCH_TIME)

            await self._terminate()
            raise AbortRun("Aborting execution")

        loop = asyncio.get_event_loop()
        for signame in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, signame),
                lambda: asyncio.ensure_future(handler(signame)))

    def _reset_signal_handlers(self):
        loop = asyncio.get_event_loop()
        for signame in self.SIGNAMES:
            loop.add_signal_handler(getattr(signal, signame),
                self._old_signal_handlers[signame])

    ## Public Interface

    @property
    def instances(self):
        # Explicitly returns the first self._num_total instances in case the
        # number of existing is more than are needed
        return (self._existing_instances + self._new_instances)[:self._num_total]

    async def terminate_instance(self, instance):
        if instance in self._new_instances:
            logging.info("Terminating new instance %s",
                instance.classic_address.public_ip)
            shutdowner = Ec2Shutdown()
            await shutdowner.shutdown([instance], terminate=True)

    ## Helpers

    async def _launch(self):
        num_new = self._num_total - len(self._existing_instances)
        if num_new > 0:
            # create config object specifically for afaws package
            options = {
                'instance_type': self._config("aws", "ec2", "instance_type"),
                'key_pair_name': self._config("aws", "ec2", "key_pair_name"),
                'security_groups': self._config("aws", "ec2", "security_groups"),
                'ebs_volume_size': self._config("aws", "ec2", "ebs", "volume_size"),
                'ebs_device_name': self._config("aws", "ec2", "ebs", "device_name"),
                'instance_initiated_shutdown_behavior': 'terminate'
            }
            launcher = Ec2Launcher(
                self._config("aws", "ec2", "image_id"),
                self._afaws_config, **options)

            name_prefix = substitude_config_wildcards(self._config, "aws",
                "ec2", "image_name_prefix_format", request_id=self._request_id)
            name_prefix = (name_prefix + '-' + str(uuid.uuid4())[:8]).strip('-')
            new_instance_names = [
                '{}-{}'.format(name_prefix, n) for n in range(num_new)
            ]

            self._new_instances = await launcher.launch(new_instance_names)

        # whether or not any instances were launched, self._launched
        # is used in signal handlers
        self._launched = True

    async def _schedule_auto_termination(self):
        minutes = self._config("aws", "ec2", "minutes_until_auto_shutdown")
        if self._new_instances and minutes:
            auto_terminator = AutoShutdownScheduler(self._config('ssh_key'))
            await auto_terminator.schedule_termination(
                self._new_instances, minutes)

    async def _initialize(self):
        if self._new_instances:
            initializer = InstanceInitializerSsh(self._config('ssh_key'),
                self._afaws_config)
            await initializer.initialize(self._new_instances)

    async def _terminate(self):
        if self._new_instances:
            for i in self._new_instances:
                i.reload()
            running_instances = [i for i in self._new_instances
                if i and i.state and i.state['Name'] in ('pending', 'running')]
            if running_instances:
                # TODO: only include instances that haven't already been shut down
                logging.info("Terminating %s new instances",
                    len(running_instances))
                await Ec2Shutdown().shutdown(running_instances, terminate=True)
            else:
                logging.info("None of the new instances are still running")
