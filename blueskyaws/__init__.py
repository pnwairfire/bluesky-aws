import json
import logging
import uuid

from afaws.config import Config as AwsConfig
from afaws.ec2.launch import Ec2Launcher
from afaws.ec2.initialization import InstanceInitializerSsh
from afaws.ec2.execute import FailedToSshError
from afaws.ec2.shutdown import Ec2Shutdown

from .config import ParallelConfig, SingleConfig

class BlueskyParallelRunner(object):

    def __init__(self, **config):
        self._config = ParallelConfig(config)

    ##
    ## Public Interface
    ##

    async def run(self, input_data):
        fires = input_data['fires']
        instances = await self._launch(len(fires))
        await self._initialize(instances)

        for fire, instance in zip(fires, instances):
            await BlueskySingleRunner(config, instance).run({'fires': [fire]})

        await self._terminate(instances)
        await self._notify()

    ##
    ## Class Initialization
    ##

    def _load_bluesky_config(self):
        config = {}
        if self._config('bluesky', 'config_file'):
            with open(self._config('bluesky', 'config_file')) as f:
                config = json.loads(f.read()).get('config')

        # Override any export config specified in the provided config file
        return config

    ##
    ## Run
    ##

    async def _launch(self, num_fires):
        # create config object specifically for afaws package
        afaws_config = AwsConfig({
            "iam_instance_profile": self._config('aws', 'iam_instance_profile'),
            "default_efs_volumes": self._config('aws', 'ec2', 'efs_volumes')
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

        u = str(uuid.uuid4())[:8]
        new_instance_names = [
            'blueskyaws-{}-{}'.format(u, n) for n in range(num_fires)
        ]

        return await launcher.launch(new_instance_names)

    async def _initialize(self, instances):
        initializer = InstanceInitializerSsh(ssh_key, afaws_config)
        await initializer.initialize(new_instances)


    async def _terminate(self, instances):
        shutdowner.shutdown(args.instance_identifiers,
            terminate=true)

    async def _notify(self):
        # TODO: send notification; send email and/or post status to an API
        #   and/or something else.
        pass


class BlueskySingleRunner(object):

    def __init__(self, config, instance):
        logging.debug("Processing fire")

        self._config = dict(config, **BLUESKY_EXPORT_CONFIG)
        self._instance = instance

    async def run(self, input_data):
        await self._run()
        await self._publish()

    async def _write_config(self):
        cmd_executer = Ec2SshExecuter(args.ssh_key, ...)
        # TODO: write bluesky config file into place

    async def _run(self):
        pass

    async def _publish(self):
        content = open('', 'rb')
        s3 = boto3.client('s3')
        s3.put_object(
           Bucket=bucket_name,
           Key='directory-in-bucket/remote-file.txt',
           Body=content
        )
