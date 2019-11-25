import uuid

from afaws.config import Config as AwsConfig
from afaws.ec2.launch import Ec2Launcher
from afaws.ec2.initialization import InstanceInitializerSsh
#from afaws.ec2.execute import FailedToSshError, Ec2SshExecuter
from afaws.ec2.shutdown import Ec2Shutdown

class Ec2InstancesManager(object):

    def __init__(self, config, num_total, existing=None):
        self._config = config
        self._afaws_config = AwsConfig({
            "iam_instance_profile": self._config('aws', 'iam_instance_profile'),
            "default_efs_volumes": self._config('aws', 'ec2', 'efs_volumes')
        })
        self._num_total = num_total
        self._existing_instances = existing
        self._new_instances = []

    async def __aenter__(self):
        await self._launch()
        await self._initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._terminate()

    ## Public Interface

    @property
    def instances(self):
        # Explicitly returns the first self._num_total instances in case the
        # number of existing is more than are needed
        return (self._existing_instances + self._new_instances)[:self._num_total]

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

            u = str(uuid.uuid4())[:8]
            new_instance_names = [
                'blueskyaws-{}-{}'.format(u, n) for n in range(num_new)
            ]

            self._new_instances = await launcher.launch(new_instance_names)

    ## Helpers

    async def _initialize(self):
        if self._new_instances:
            initializer = InstanceInitializerSsh(self._config('ssh_key'),
                self._afaws_config)
            await initializer.initialize(self._new_instances)


    async def _terminate(self):
        if self._new_instances:
            shutdowner = Ec2Shutdown()
            await shutdowner.shutdown(self._new_instances, terminate=True)
