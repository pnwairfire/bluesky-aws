import asyncio
import datetime
import json
import logging
import os
import re
import tempfile
import uuid

import afconfig
import boto3
from afaws.ec2.ssh import SshClient
from afaws.asyncutils import run_in_loop_executor

from .input import InputLoader
from .launch import Ec2InstancesManager
from .config import Config, BLUESKY_EXPORT_CONFIG, substitude_config_wildcards
from .status import SystemState, Status, StatusTracker

__all__ = [
    "BlueskyParallelRunner"
]


class BlueskyParallelRunner(object):
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
        self._config = Config(config)
        self._s3_client = boto3.client('s3')

    ##
    ## Public Interface
    ##

    async def run(self, input_file_name):
        self._utcnow = datetime.datetime.utcnow()
        self._set_request_id(input_file_name)

        await self._set_status_tracker()
        async with InputLoader(self._config, input_file_name, self._status_tracker) as input_loader:
            self._input_loader = input_loader
            self._set_instances_needed()
            await self._load_bluesky_config()
            await self._record_input()
            await self._run_all()
            await self._notify()

    ## Initialization

    JSON_EXT_STRIPPER = re.compile('\.json$')

    def _set_request_id(self, input_file_name):
        if self._config('request_id_format'):
            self._request_id = substitude_config_wildcards(self._config,
                'request_id_format', uuid=str(uuid.uuid4()).split('-')[0],
                utc_today=self._utcnow.strftime("%Y%m%d"),
                utc_now=self._utcnow.strftime("%Y%m%dT%H%M%S"))
        else:
            self._request_id = self.JSON_EXT_STRIPPER.sub('',
                os.path.basename(input_file_name))

    async def _set_status_tracker(self):
        self._status_tracker = StatusTracker(
            self._request_id, self._s3_client, self._config)
        await self._status_tracker.initialize()

    def _set_instances_needed(self):
        num_fires = len(self._input_loader.fires)
        self._total_instances_needed = min(num_fires,
            self._config("aws", 'ec2', "max_num_instances") or num_fires)

    async def _load_bluesky_config(self):
        self._bluesky_config = {'config': {}}

        # First load config file, if specified
        if self._config('bluesky', 'config_file'):
            with open(self._config('bluesky', 'config_file')) as f:
                self._bluesky_config = json.loads(f.read())

        # Then apply any overrides specified in the bluesky-aws config file
        # or on the command line
        if self._config('bluesky', 'config'):
            # merges in place
            afconfig.merge_configs(self._bluesky_config['config'],
                self._config('bluesky', 'config'))

        # Finally, override export config what hardcoded value
        # TODO: allow user config to include export settings and
        #   merge BLUESKY_EXPORT_CONFIG into them?
        self._bluesky_config['config'].update(BLUESKY_EXPORT_CONFIG)

    async def _record_input(self):
        await run_in_loop_executor(self._s3_client.upload_file,
            self._input_loader.local_input_file_name,
            self._config('aws', 's3', 'bucket_name'),
            os.path.join('requests', self._request_id + '.json'))

    async def _run_all(self):
        ec2_instance_manager = Ec2InstancesManager(self._config,
            self._total_instances_needed, self._request_id,
            existing=self._instances)
        async with ec2_instance_manager:
            # TODO: Add more options for supporting the case where
            #     num_fires > num_instances; Some possibilities:
            #       1) take the first num_instances fires, given the order the
            #          fires are specified in the input data
            #          ***(this is the current implementation***)
            #       2) somehow prioritize fires and run only first
            #          num_instances fires
            #       3) tranche fires, one tranche per instance, and within
            #          each tranche, execute one of the following:
            #            a) separate runs sequentially
            #            b) separate runs in parallel
            #            c) single run
            runs = zip(self._input_loader.fires, ec2_instance_manager.instances)
            runners = [
                BlueskySingleRunner({'fires': [fire]}, instance, self._config,
                    self._bluesky_config, self._request_id,
                    self._status_tracker)
                for fire, instance in runs
            ]

            await asyncio.gather(*[
                runner.run() for runner in runners
            ])

            await self._status_tracker.set_system_state(SystemState.COMPLETE)



    ## Notifications

    async def _notify(self):
        # TODO: send notification; send email and/or post status to an API
        #   and/or something else.
        pass


class BlueskySingleRunner(object):

    def __init__(self, input_data, instance, config, bluesky_config,
            request_id, status_tracker, utcnow=None):
        self._utcnow = utcnow or datetime.datetime.utcnow()
        self._input_data = input_data
        self._instance = instance
        self._config = config
        self._bluesky_config = bluesky_config
        self._request_id = request_id
        self._status_tracker = status_tracker
        self._set_run_id()

    ## Public Interface

    async def run(self):
        ip = self._instance.classic_address.public_ip
        logging.info("Running bluesky on %s", ip)

        try:
            with SshClient(self._config('ssh_key'), ip) as ssh_client:
                self._ssh_client = ssh_client
                await self._create_remote_dirs()
                await self._write_remote_files()
                await self._install_bluesky_and_dependencies()
                # TODO: check for met and wait until it arrives,
                #   setting system status to WAITING
                await self._run_bluesky()
                await self._tarball()
                await self._upload_aws_credentials()
                await self._publish()
                await self._cleanup()
            # TODO: check return value of bluesky and/or look in bluesky
            #   output for error, and determine status from that
            await self._status_tracker.set_run_status(self, Status.SUCCESS,
                output_url=self._s3_url(self._config('aws', 's3', 'output_path'), 'tar.gz'),
                log_url=self._s3_url('log', 'log'))

        except Exception as e:
            # TODO: determine error, if possible
            await self._status_tracker.set_run_status(self, Status.UNKNOWN,
                message=str(e))


    ## Run Helpers

    def _get_fire_id(self):
        if len(self._input_data['fires']) == 1 and self._input_data['fires'][0].get('id'):
            return self._input_data['fires'][0]['id']


    def _set_run_id(self):
        # if run_id_format is not defined, set run id to fire id, if
        # only one fire, else set to new uuid (?)
        fire_id = self._get_fire_id()
        if self._config('run_id_format'):
            run_id = substitude_config_wildcards(self._config, 'run_id_format',
                fire_id=fire_id or '', request_id=self._request_id,
                uuid=str(uuid.uuid4()).split('-')[0],
                utc_today=self._utcnow.strftime("%Y%m%d"),
                utc_now=self._utcnow.strftime("%Y%m%dT%H%M%S"))
            self._run_id = self._utcnow.strftime(run_id)
        else:
            self._run_id = "fire-" + fire_id if fire_id else str(uuid.uuid4())

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
        # create dir, in case it doesn't already exist
        self._host_data_dir = os.path.join(self._remote_home_dir,
            "data/bluesky/", self._run_id)
        await self._execute("mkdir -p {}".format(self._host_data_dir))
        # clear out any old output, if there is any
        await self._execute("rm -r {}".format(
            os.path.join(self._host_data_dir, '*')))

    async def _write_remote_files(self):
        await self._write_remote_json_file(self._bluesky_config,
            os.path.join(self._host_data_dir, 'config.json'))
        await self._write_remote_json_file(self._input_data,
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
        cmd = "docker run --rm -v {host_data_dir}:/data/bluesky/".format(
            host_data_dir=self._host_data_dir)

        for v in self._config('aws', 'ec2', 'efs_volumes'):
            cmd += " -v {d}:{d}".format(d=v[1])

        cmd += (" pnwairfire/bluesky:{version}"
            " bsp --log-level=DEBUG"
            " --run-id={run_id}"
            " -c /data/bluesky/config.json"
            " -i /data/bluesky/input.json"
            " -o /data/bluesky/output.json"
            " --log-file /data/bluesky/output.log"
            " {modules}"
            ).format(
                version=self._config('bluesky_version'),
                run_id=self._run_id,
                modules=' '.join(self._config('bluesky', 'modules') + ['export'])
            )
        if self._config('bluesky', 'today'):
            cmd += " --today {}".format(self._config('bluesky', 'today'))

        return cmd

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
        cmd = ("aws s3 cp {host_data_dir}/exports/{run_id}.tar.gz "
            "s3://{bucket}/{output_path}/{request_id}/{run_id}.tar.gz").format(
                host_data_dir=self._host_data_dir, run_id=self._run_id,
                bucket=self._config('aws', 's3', 'bucket_name'),
                output_path=self._config('aws', 's3', 'output_path').strip('/'),
                request_id=self._request_id)
        await self._execute(cmd)

        # Pushes log file from remote ec2 instance to s3
        cmd = ("aws s3 cp {host_data_dir}/output.log "
            "s3://{bucket}/log/{request_id}/{run_id}.log").format(
                host_data_dir=self._host_data_dir, run_id=self._run_id,
                bucket=self._config('aws', 's3', 'bucket_name'),
                request_id=self._request_id)
        await self._execute(cmd)

    async def _cleanup(self):
        if self._config('cleanup_output'):
            # delete the entire output dir
            await self._execute("rm -r {}".format(self._host_data_dir))


    REGION = "us-west-2" # TODO: don't hard code this

    def _s3_url(self, path, extension):
         return ("https://{bucket}.s3-{region}.amazonaws.com/{path}/"
            "{request_id}/{run_id}.{ext}").format(
                bucket=self._config('aws', 's3', 'bucket_name'),
                region=self.REGION, path=path.strip('/'),
                request_id=self._request_id, run_id=self._run_id,
                ext=extension)
