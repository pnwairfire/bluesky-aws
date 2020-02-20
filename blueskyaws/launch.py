import asyncio
import logging
import signal
import uuid

from afaws.config import Config as AwsConfig
from afaws.ec2.launch import Ec2Launcher
from afaws.ec2.initialization import InstanceInitializerSsh
#from afaws.ec2.execute import FailedToSshError, Ec2SshExecuter
from afaws.ec2.shutdown import Ec2Shutdown

from .config import substitude_config_wildcards

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

    async def __aenter__(self):
        self._set_signal_handlers()
        await self._launch()
        await self._initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._terminate()
        self._reset_signal_handlers(reset=True)

    SIGNAMES = ('SIGINT', 'SIGTERM')

    def _set_signal_handlers(self, reset=False):
        self._old_signal_handlers = {
            s: signal.getsignal(getattr(signal, s)) for s in self.SIGNAMES
        }

        async def handler(signame):
            logging.info("Receieved signal %s. Terminating "
                "instances and then aborting", signame)
            await self._terminate()
            raise RuntimeError("Aborting execution")

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
                'ebs_device_name': self._config("aws", "ec2", "ebs", "device_name")
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
                if i and i.state and i.state['Name'] == 'running']
            if running_instances:
                # TODO: only include instances that haven't already been shut down
                logging.info("Terminating %s new instances",
                    len(running_instances))
                await Ec2Shutdown().shutdown(running_instances, terminate=True)
            else:
                logging.info("None of the new instances are still running")
