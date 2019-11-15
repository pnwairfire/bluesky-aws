import logging

from afaws.ec2.launch import Ec2Launcher
from afaws.ec2.initialization import InstanceInitializerSsh
from afaws.ec2.execute import FailedToSshError
from afaws.config import Config as AwsConfig

from .config import Config

class BlueskyRunner(object):

    def __init__(self, **config):
        self._config = Config(config)

    async def run(self, input_data):
        fires = input_data['fires']
        instances = await self._launch(len(fires))
        await self._initialize(instances)

        for fire, instance in zip(fires, instances):
            await BlueskySingleFireRunner(fire, instnace).run()

        logging.debug("Processing fire")
        await self._run()
        await self._publish()
        await self._terminate(instances)
        await self._notify()
        # TODO: send notification; send email and/or post status to an API
        #   and/or something else.

    async def _launch(num_fires):
        # create config object specifically for afaws package
        afaws_config = AwsConfig({
            "iam_instance_profile": self._config('aws', 'iam_instance_profile'),
            "default_efs_volumes": self._config('aws', 'ec2', 'default_efs_volumes')
        })
        options = {
            'instance_type': self._config("aws", "ec2", "instance_type"),
            'key_pair_name': self._config("aws", "ec2", "key_pair_name"),
            'security_groups': self._config("aws", "ec2", "security_groups"),
            'ebs_volume_size': self._config("aws", "ec2", "ebs", "volume_size")
        }
        launcher = Ec2Launcher(
            self._config("aws", "ec2", "image_id"),
            afaws_config, **options)

        return await launcher.launch(args.new_instance_names)

    async def _initialize(self, instances):
        initializer = InstanceInitializerSsh(ssh_key, afaws_config)
        await initializer.initialize(new_instances)
        if self._config('bluesky', 'config_file'):
            # TODO: copy bluesky config file into place
            pass

    async def _terminate(self, instances):
        pass


class BlueskySingleFireRunner(object):

    def __init__(self, fire, instance):
        self._fires = fire
        self._instance = instance

    async def run(self):
        await self._run()
        await self._publish()

    async def _run(self):
        pass

    async def _publish(self):
        pass
