import abc
import datetime
import json
import logging
import os
import tempfile
import uuid

from afaws.config import Config as AwsConfig
from afaws.ec2.launch import Ec2Launcher
from afaws.ec2.initialization import InstanceInitializerSsh
#from afaws.ec2.execute import FailedToSshError, Ec2SshExecuter
from afaws.ec2.shutdown import Ec2Shutdown
from afaws.ec2.ssh import SshClient

from .config import ParallelConfig, SingleConfig, BLUESKY_EXPORT_CONFIG

class BaseBlueskyRunner(abc.ABC):

    def __init__(self, *args, **config):
        self._config = self.config_class(config)
        self._afaws_config = AwsConfig({
            "iam_instance_profile": self._config('aws', 'iam_instance_profile'),
            "default_efs_volumes": self._config('aws', 'ec2', 'efs_volumes')
        })

    @property
    @abc.abstractmethod
    def config_class(self):
        return Config


class BlueskyParallelRunner(BaseBlueskyRunner):

    def __init__(self, **config):
        super().__init__(**config)

    @property
    def config_class(self):
        return ParallelConfig

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
    ## Run
    ##

    async def _launch(self, num_fires):
        # create config object specifically for afaws package
        options = {
            'instance_type': self._config("aws", "ec2", "instance_type"),
            'key_pair_name': self._config("aws", "ec2", "key_pair_name"),
            'security_groups': self._config("aws", "ec2", "security_groups"),
            'ebs_volume_size': self._config("aws", "ec2", "ebs", "volume_size")
        }
        launcher = Ec2Launcher(
            self._config("aws", "ec2", "image_id"),
            self._afaws_config, **options)

        u = str(uuid.uuid4())[:8]
        new_instance_names = [
            'blueskyaws-{}-{}'.format(u, n) for n in range(num_fires)
        ]

        return await launcher.launch(new_instance_names)

    async def _initialize(self, instances):
        initializer = InstanceInitializerSsh(self._config('ssh_key'),
            self._afaws_config)
        await initializer.initialize(new_instances)


    async def _terminate(self, instances):
        shutdowner.shutdown(args.instance_identifiers,
            terminate=true)

    async def _notify(self):
        # TODO: send notification; send email and/or post status to an API
        #   and/or something else.
        pass


class BlueskySingleRunner(BaseBlueskyRunner):

    def __init__(self, instance, **config):
        super().__init__(**config)
        self._instance = instance

    @property
    def config_class(self):
        return SingleConfig

    ##
    ## Public Interface
    ##

    async def run(self, input_data):
        self._run_id = self._config('run_id_format').format(
            uuid=str(uuid.uuid4()).split('-')[0])
        self._run_id = datetime.datetime.utcnow().strftime(self._run_id)
        logging.info("Running")
        ip = self._instance.classic_address.public_ip
        with SshClient(self._config('ssh_key'), ip) as ssh_client:
            self._ssh_client = ssh_client
            await self._load_bluesky_config()
            await self._create_remote_dirs()
            await self._write_remote_files(input_data)
            await self._install_bluesky()
            await self._run()
            await self._tarball()
            await self._publish()

    ##
    ## Run Helpers
    ##

    async def _load_bluesky_config(self):
        # Note that the bluesky config is loaded in BlueskySingleRunner
        # instead of in BlueskyParallelRunner to facilitate single-run mode,
        # in which BlueskySingleRunner is used directly by bin/run-bluesky.
        # This does mean that the config will be loaded N+1 redundant times
        # in paralle runs for N fires, but performance and run time hit
        # should be insignificant for most if not all uses of this package.
        self._bluesky_config = {'config': {}}
        if self._config('bluesky', 'config_file'):
            with open(self._config('bluesky', 'config_file')) as f:
                self._bluesky_config = json.loads(f.read()).get('config')

        # Override any export config specified in the provided config file
        self._bluesky_config['config'].update(BLUESKY_EXPORT_CONFIG)

    async def _execute(self, cmd):
        stdin, stdout, stderr = await self._ssh_client .execute(cmd)
        stderr = stderr.read().decode().strip()
        stdout = stdout.read().decode().strip()
        if stderr:
            logging.error("Error running command %s:  %s", cmd, stderr)

        return stdout

    async def _create_remote_dirs(self):
        home_dir = await self._execute('echo $HOME')
        # TODO: handle home_dir == None
        self._host_data_dir = os.path.join(home_dir, "data/bluesky/")
        await self._execute("mkdir -p {}".format(self._host_data_dir))

    async def _write_remote_files(self, input_data):
        await self._write_remote_json_file(self._bluesky_config,
            os.path.join(self._host_data_dir, 'config.json'))
        await self._write_remote_json_file(input_data,
            os.path.join(self._host_data_dir, 'input.json'))

    async def _write_remote_json_file(self, data, remote_file_path):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(json.dumps(data))
            f.flush()
            await self._ssh_client.put(f.name, remote_file_path)

    async def _install_bluesky(self):
        await self._execute("docker pull pnwairfire/bluesky:{}".format(
            self._config('bluesky_version')))

    async def _run(self):
        cmd = self._form_bsp_command()
        await self._execute(cmd)
        await self._execute('sudo chown -R $USER:$USER {}'.format(
            self._host_data_dir))

    def _form_bsp_command(self):
        return ("docker run --rm -v {host_data_dir}:/data/bluesky/"
            " pnwairfire/bluesky:{version}"
            " bsp --log-level=DEBUG"
            " --run-id={run_id}"
            " -c /data/bluesky/config.json"
            " -i /data/bluesky/input.json"
            " -o /data/bluesky/output.json"
            " --log-file /data/bluesky/output.log"
            " {modules}"
            ).format(
                host_data_dir=self._host_data_dir,
                version=self._config('bluesky_version'),
                run_id=self._run_id,
                modules=' '.join(self._config('bluesky', 'modules') + ['export'])
            )

    async def _tarball(self):
        await self._execute(("cd {host_data_dir}/exports/; tar czf "
            " {run_id}.tar.gz {run_id}").format(
            host_data_dir=self._host_data_dir, run_id=self._run_id))

    async def _publish(self):
        # TODO: upload to s3
        # content = open('', 'rb')
        # s3 = boto3.client('s3')
        # s3.put_object(
        #    Bucket=bucket_name,
        #    Key='directory-in-bucket/remote-file.txt',
        #    Body=content
        # )
        pass
