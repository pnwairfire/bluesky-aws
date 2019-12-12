import asyncio
import datetime
import json
import logging
import os
import re
import tempfile
import uuid

import boto3
from afaws.ec2.ssh import SshClient
from afaws.asyncutils import run_in_loop_executor

from .launch import Ec2InstancesManager
from .config import (
        Config, ParallelConfig, SingleConfig, BLUESKY_EXPORT_CONFIG
)

__all__ = [
    "BlueskyParallelRunner"
]


class Status(object):
    # Used in overal stats
    COMPLETE = 'complete'

    # Assigned to individual runs
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'


class BlueskyParallelRunner(object):
    """Given a pool of existing instances along with instances
    to be launced, runs bluesky on a set of fires in as parallel a
    fashion as is allowed (based on configuration settings dictating
    how many instances may be used).
    """

    def __init__(self, instances=None, **config):
        self._utcnow = datetime.datetime.utcnow()
        self._instances = instances
        # A more restrictive config object will be created from the
        # unrestricted Conig object based on whether or not new
        # instances are needed for the number of fires passed into run
        self._raw_config = Config(config)
        self._s3_client = boto3.client('s3')

    ##
    ## Public Interface
    ##

    async def run(self, input_file_name):
        self._load_input(input_file_name)
        self._set_config()
        self._set_request_id(input_file_name)
        await self._record_input(input_file_name)

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
            runs = zip(self._fires, ec2_instance_manager.instances)
            runners = [
                BlueskySingleRunner({'fires': [fire]}, instance,
                    self._config, self._request_id,
                    self._update_single_run_status)
                for fire, instance in runs
            ]

            await self._initialize_status(runners)

            await asyncio.gather(*[
                runner.run() for runner in runners
            ])

        await self._finalize_status()

        await self._notify()

    ## Initialization

    JSON_EXT_STRIPPER = re.compile('\.json$')

    def _load_input(self, input_file_name):
        with open(input_file_name, 'r') as f:
            # reset point to beginning of file and load json data
            f.seek(0)
            self._fires = json.loads(f.read())['fires']

    def _set_config(self):
        num_fires = len(self._fires)
        self._total_instances_needed = min(num_fires,
            self._raw_config("aws", 'ec2', "max_num_instances") or num_fires)

        if self._total_instances_needed > len(self._instances):
            self._config = ParallelConfig(self._raw_config)
        else:
            self._config = SingleConfig(self._raw_config)

    def _set_request_id(self, input_file_name):
        if self._config('request_id_format'):
            self._request_id = self._config('request_id_format').format(
                uuid=str(uuid.uuid4()).split('-')[0],
                utc_today=self._utcnow.strftime("%Y%m%d"),
                utc_now=self._utcnow.strftime("%Y%m%dT%H%M%S"))
        else:
            base_name = os.path.basename(input_file_name)
            self._request_id = self.JSON_EXT_STRIPPER.sub('', base_name)


    async def _record_input(self, input_file_name):
        await run_in_loop_executor(self._s3_client.upload_file,
            input_file_name, self._config('aws', 's3', 'bucket_name'),
            os.path.join('requests', self._request_id + '.json'))


    ## Status

    async def _save_status(self):
        await run_in_loop_executor(self._s3_client.put_object,
            Body=json.dumps(self._status),
            Bucket=self._config('aws', 's3', 'bucket_name'),
            Key=os.path.join('status', self._request_id + '-status.json'))

    async def _initialize_status(self, runners):
        self._status = {
            "status": Status.RUNNING,
            "counts": {
                Status.RUNNING: len(self._fires),
                Status.SUCCESS: 0,
                Status.FAILURE: 0,
                Status.COMPLETE: 0
            },
            "runs": {
                runner._run_id: {
                    "status": Status.RUNNING,
                    "message": None
                } for runner in runners
            }
        }
        await self._save_status()

    async def _update_single_run_status(self, run, status, message=None):
        # Update run's status
        self._status["runs"][run._run_id]["status"] = status
        self._status["runs"][run._run_id]["message"] = message

        # Update count for this status, if it has a count
        if status in self._status['counts']:
            self._status['counts'][status] += 1

        # update running and complete counts, if appropriate
        if status in (Status.SUCCESS, Status.FAILURE):
            self._status['counts'][Status.RUNNING] -= 1
            self._status['counts'][Status.COMPLETE] += 1

        await self._save_status()

    async def _finalize_status(self):
        self._status['status'] = Status.COMPLETE
        await self._save_status()


    ## Notifications

    async def _notify(self):
        # TODO: send notification; send email and/or post status to an API
        #   and/or something else.
        pass


class BlueskySingleRunner(object):

    def __init__(self, input_data, instance, config,
            request_id, update_single_run_status_func, utcnow=None):
        self._utcnow = utcnow or datetime.datetime.utcnow()
        self._input_data = input_data
        self._instance = instance
        self._config = config
        self._request_id = request_id
        self._update_single_run_status = update_single_run_status_func
        self._set_run_id()

    ## Public Interface

    async def run(self):
        ip = self._instance.classic_address.public_ip
        logging.info("Running bluesky on %s", ip)
        with SshClient(self._config('ssh_key'), ip) as ssh_client:
            self._ssh_client = ssh_client
            await self._load_bluesky_config()
            await self._create_remote_dirs()
            await self._write_remote_files()
            await self._install_bluesky_and_dependencies()
            await self._run_bluesky()
            await self._tarball()
            await self._upload_aws_credentials()
            await self._publish()
            await self._cleanup()
        # TODO: check return value of bluesky and/or look in bluesky
        #   output for error, and determine status from that
        await self._update_single_run_status(self, Status.SUCCESS)

    ## Run Helpers

    def _get_fire_id(self):
        if len(self._input_data['fires']) == 1 and self._input_data['fires'][0].get('id'):
            return self._input_data['fires'][0]['id']


    def _set_run_id(self):
        # if run_id_format is not defined, set run id to fire id, if
        # only one fire, else set to new uuid (?)
        fire_id = self._get_fire_id()
        if self._config('run_id_format'):
            run_id = self._config('run_id_format').format(
                request_id=self._request_id,
                uuid=str(uuid.uuid4()).split('-')[0],
                fire_id=fire_id or '',
                utc_today=self._utcnow.strftime("%Y%m%d"),
                utc_now=self._utcnow.strftime("%Y%m%dT%H%M%S"))
            self._run_id = self._utcnow.strftime(run_id)
        else:
            self._run_id = "fire-" + fire_id if fire_id else str(uuid.uuid4())

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
                self._bluesky_config = json.loads(f.read())

        # Override any export config specified in the provided config file
        # TODO: allow user config to include export settings and
        #   merge BLUESKY_EXPORT_CONFIG into them?
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
            "s3://{bucket}/log/{request_id}.log").format(
                host_data_dir=self._host_data_dir,
                bucket=self._config('aws', 's3', 'bucket_name'),
                request_id=self._request_id)
        await self._execute(cmd)

    async def _cleanup(self):
        if self._config('cleanup_output'):
            # delete the entire output dir
            await self._execute("rm -r {}".format(self._host_data_dir))
