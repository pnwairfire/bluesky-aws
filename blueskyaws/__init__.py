import datetime
import json
import logging
import os
import tempfile
import uuid

from afaws.ec2.launch import Ec2Launcher
from afaws.ec2.initialization import InstanceInitializerSsh
#from afaws.ec2.execute import FailedToSshError, Ec2SshExecuter
from afaws.ec2.shutdown import Ec2Shutdown
from afaws.ec2.ssh import SshClient

from .launch import Ec2InstancesManager
from .config import (
        Config, ParallelConfig, SingleConfig, BLUESKY_EXPORT_CONFIG
)

class BaseBlueskyRunner(object):
    """Given a pool of existing instances along with instances
    to be launced, runs bluesky on a set of fires in as parallel a
    fashion as is allowed (based on configuration settings dictating
    how many instances may be used).
    """

    def __init__(self, instances=None, **config):
        self._instances = instances
        # A more restrictive config object will be created from the
        # unrestricted Conig object based on whether or not new
        # instances are needed for the number of fires passed into run
        self._raw_config = Config()

    ##
    ## Public Interface
    ##

    async def run(self, input_file):
        self._load(input_file)
        self._set_config()
        await self._initialize_stats(fires)

        ec2_instance_manager = Ec2InstancesManager(self._config,
            self._total_instances_needed, existing=self._instances)
        async with ec2_instance_manager:
            for fire, instance in zip(fires, manager.instances):
                await BlueskySingleRunner(instance, config).run({'fires': [fire]})

        await self._notify()

    def _load_input(self, input_file):
        with open(input_file, 'r') as f:
            self._fires = json.loads(f.read())


    def _set_config(self, fires):
        max_num_instances = self._raw_config("aws", 'ec2', "max_num_instances")
        self._total_instances_needed = min(max_num_instances, len(fires))

        if self._total_instances_needed > len(self._instances):
            self._config = ParallelConfig(self._raw_config)
        else:
            self._config = SingleConfig(self._raw_config)

    ##
    ## Helpers
    ##

    def _initialize_status(self, fires):
        pass

    def _update_status(self, fire, status):
        pass

    async def _notify(self):
        # TODO: send notification; send email and/or post status to an API
        #   and/or something else.
        pass


class BlueskySingleRunner(object):

    def __init__(self, instance, config):
        self._instance = instance
        self._config = config

    ##
    ## Public Interface
    ##

    async def run(self, input_data):
        # TODO: if run_id is not defined, set run id to fire id, if
        #   only one fire, else set to new uuid (?)
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
            await self._install_bluesky_and_dependencies()
            await self._run_bluesky()
            await self._tarball()
            await self._upload_aws_credentials()
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
        self._remote_home_dir = await self._execute('echo $HOME')
        # TODO: handle self._remote_home_dir == None
        self._host_data_dir = os.path.join(self._remote_home_dir, "data/bluesky/")
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

    async def _install_bluesky_and_dependencies(self):
        # Note: it's advised to have these pre-installed on the
        #    ec2 instance, but this is just in case they're not
        await self._execute("docker pull pnwairfire/bluesky:{}".format(
            self._config('bluesky_version')))

        # Note: these installation commands are ubuntu/debian specific
        if not (await self._execute("which aws")):
            await self._execute("sudo apt -y install awscli")

        if not (await self._execute("which docker")):
            await self._execute('sudo apt update')
            await self._execute('sudo apt install -y apt-transport-https ca-certificates curl software-properties-common')
            await self._execute('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -')
            await self._execute('sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"')
            await self._execute('sudo apt update')
            await self._execute('apt-cache policy docker-ce')
            await self._execute('sudo apt install -y docker-ce')

    async def _run_bluesky(self):
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

    async def _upload_aws_credentials(self):
        # Credentials are uploaded in order to push to s3
        remote_aws_dir = os.path.join(self._remote_home_dir, ".aws")
        if not await self._execute('ls {}'.format(remote_aws_dir)):
            local_aws_dir = os.path.join(os.environ["HOME"], ".aws/")
            # TODO: if recursive put fails, update put/get to support it
            await self._ssh_client.put(local_aws_dir, remote_aws_dir)

    async def _publish(self):
        # Pushes output bundle from remote ec2 instance to s3
        cmd = "aws s3 cp {host_data_dir}/exports/{run_id}.tar.gz s3://{bucket}/".format(
            host_data_dir=self._host_data_dir, run_id=self._run_id,
            bucket=self._config('aws', 's3', 'bucket_name'))
        await self._execute(cmd)
