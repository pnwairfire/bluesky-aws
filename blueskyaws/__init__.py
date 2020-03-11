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
            await self._record_config(self._config, 'bluesky-aws')
            await self._record_config(self._bluesky_config, 'bluesky')
            await self._run_all()
            await self._notify()

    ## Initialization

    JSON_EXT_STRIPPER = re.compile('\.json$')

    def _set_request_id(self, input_file_name):
        input_file_basename = self.JSON_EXT_STRIPPER.sub('',
                os.path.basename(input_file_name))
        if self._config('request_id_format'):
            request_id = substitude_config_wildcards(self._config,
                'request_id_format', uuid=str(uuid.uuid4()).split('-')[0],
                utc_today=self._utcnow.strftime("%Y%m%d"),
                utc_now=self._utcnow.strftime("%Y%m%dT%H%M%S"),
                input_file_name=input_file_basename)
            self._request_id = self._utcnow.strftime(request_id)

        else:
            self._request_id = input_file_basename

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
                c = json.loads(f.read())
                logging.debug("bluesky configuration from bluesky config file: %s", c)
                self._bluesky_config = c

        # Then apply any overrides specified in the bluesky-aws config file
        # or on the command line
        if self._config('bluesky', 'config'):
            # merges in place
            logging.debug("bluesky configuration from blueskyaws config file: %s",
                self._config('bluesky', 'config'))
            afconfig.merge_configs(self._bluesky_config['config'],
                self._config('bluesky', 'config'))

        # Then apply any run_config specified in the input file
        if self._input_loader.bluesky_config:
            logging.debug("bluesky configuration from blueskyaws input file: %s",
                self._input_loader.bluesky_config)
            afconfig.merge_configs(self._bluesky_config['config'],
                self._input_loader.bluesky_config)

        # Finally, override export config with hardcoded value
        # TODO: allow user config to include export settings and
        #   merge BLUESKY_EXPORT_CONFIG into them?
        self._bluesky_config['config'].update(BLUESKY_EXPORT_CONFIG)

    async def _record_input(self):
        await run_in_loop_executor(self._s3_client.upload_file,
            self._input_loader.local_input_file_name,
            self._config('aws', 's3', 'bucket_name'),
            os.path.join('requests', self._request_id + '.json'))

    async def _record_config(self, config, config_type):
        if hasattr(config, 'to_dict'):
            config = config.to_dict()

        await run_in_loop_executor(self._s3_client.put_object,
            Body=json.dumps(config),
            Bucket=self._config('aws', 's3', 'bucket_name'),
            Key=os.path.join('config', self._request_id + '-config-'
                + config_type + '.json'))

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
                BlueskySingleRunner({'fires': [fire]}, ec2_instance_manager,
                    instance, self._config, self._bluesky_config,
                    self._request_id, self._status_tracker, self._utcnow)
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

    def __init__(self, input_data, ec2_instance_manager, instance, config,
            bluesky_config, request_id, status_tracker, request_utcnow):
        self._input_data = input_data
        self._ec2_instance_manager = ec2_instance_manager
        self._instance = instance
        self._ip = self._instance.classic_address.public_ip
        self._config = config
        self._bluesky_config = bluesky_config
        self._request_id = request_id
        self._status_tracker = status_tracker
        # Default bluesky's '--today' to the requests's 'now', so that all
        # bsp runs are executed with the same value.  But, also create
        # a run-specific 'now' for use in formating the 'run_id'.
        self._bluesky_today_str = (config('bluesky', 'today')
            or request_utcnow.strftime('%Y-%m-%d'))
        self._utcnow = datetime.datetime.utcnow()
        self._set_run_id()
        self._output_url = None
        self._log_url = None
        logging.info("Run %s will be executed on %s", self._run_id, self._ip)

    ## Public Interface

    async def run(self):
        await self._record_input()
        await self._status_tracker.set_run_status(self, Status.RUNNING,
            fire_info=self._get_fire_info())
        logging.info("Running BlueskySingleRunner.run on %s", self._ip)

        try:
            with SshClient(self._config('ssh_key'), self._ip) as ssh_client:
                try:
                    self._ssh_client = ssh_client
                    await self._create_remote_dirs()
                    await self._write_remote_files()
                    await self._install_bluesky_and_dependencies()
                    # TODO: check for met and wait until it arrives,
                    #   setting system status to WAITING until is available
                    await self._run_bluesky()
                    await self._tarball()
                    await self._upload_aws_credentials()
                    await self._publish_output()
                    await self._publish_log()
                    await self._cleanup()

                except Exception as e:
                    logging.error(str(e), exc_info=True)
                    await self._status_tracker.set_run_status(self,
                        Status.UNKNOWN, message=str(e),
                        output_url=self._output_url, log_url=self._log_url)

                else:
                    # TODO: also check return value of bsp to detect
                    #    failure, if possible
                    error = await self._check_output_for_error()
                    status = Status.FAILURE if error else Status.SUCCESS
                    status_kwargs = dict(
                        output_url=self._output_url,
                        log_url=self._log_url
                    )
                    if error:
                        status_kwargs.update(error=error)
                    await self._status_tracker.set_run_status(self,
                        status, **status_kwargs)

        except Exception as e:
            logging.error(str(e), exc_info=True)
            # TODO: determine error, if possible
            await self._status_tracker.set_run_status(self, Status.UNKNOWN,
                message=str(e))

        finally:
            await self._ec2_instance_manager.terminate_instance(self._instance)


    @property
    def run_id(self):
        return self._run_id


    ## Run Helpers

    def _get_fire_id(self):
        if len(self._input_data['fires']) == 1 and self._input_data['fires'][0].get('id'):
            return self._input_data['fires'][0]['id']

    def _get_fire_info(self):
        fire_info = {
            'area': None,
            'lat': None,
            'lng': None
        }
        try:
            area = 0
            for a in self._input_data['fires'][0]['activity']:
                for aa in a['active_areas']:
                    if 'specified_points' in aa:
                        for sp in aa['specified_points']:
                            area += sp['area']
                            if not fire_info['lat']:
                                fire_info.update(
                                    lat=sp['lat'],
                                    lng=sp['lng']
                                )
                    elif 'perimeter' in aa:
                        area += aa['perimeter'].get('area', 0)
                        if not fire_info['lat']:
                            first_coord = aa['perimeter']['polygon'][0]
                            fire_info.update(
                                lat=first_coord[1],
                                lng=first_coord[0]
                            )
            fire_info['area'] = area

        except Exception as e:
            logging.warn("Failed to parse fire info from input file")

        return fire_info

    def _set_run_id(self):
        # if run_id_format is not defined, set run id to fire id, if
        # only one fire, else set to new uuid (?)
        fire_id = self._get_fire_id()
        if self._config('run_id_format'):
            run_id = substitude_config_wildcards(self._config, 'run_id_format',
                fire_id=fire_id or '', request_id=self._request_id,
                uuid=str(uuid.uuid4()).split('-')[0],
                utc_today=self._utcnow.strftime("%Y%m%d"),
                utc_now=self._utcnow.strftime("%Y%m%dT%H%M%S"),
                bluesky_today=self._bluesky_today_str.replace('-',''))
            self._run_id = self._utcnow.strftime(run_id)
        else:
            self._run_id = "fire-" + fire_id if fire_id else str(uuid.uuid4())

    async def _record_input(self):
        await run_in_loop_executor(boto3.client('s3').put_object,
            Body=json.dumps(self._input_data),
            Bucket=self._config('aws', 's3', 'bucket_name'),
            Key=os.path.join('input', self._request_id,
                self._run_id + '-input.json'))

    async def _execute(self, cmd, ignore_errors=False):
        # need to pass ignore_errors into self._ssh_client.execute to ignore
        # non-zero return codes, and then use it below to ignore stderr
        result = await self._ssh_client.execute(cmd, ignore_errors=ignore_errors)
        logging.info("Just executed %s", cmd)

        # TODO: check result.return_code in addition to or instead of result.stderr
        if result.stderr:
            msg = "Error running command {}:  {}".format(cmd, result.stderr)
            if ignore_errors:
                # just log error
                logging.error(msg, exc_info=True)
            else:
                raise RuntimeError(msg)

        # TODO: remove the .rstrip('\n') if afaws is updated to do so
        return result.stdout.rstrip('\n')

    async def _create_remote_dirs(self):
        logging.info("Creating remote dirs on %s", self._ip)
        self._remote_home_dir = await self._execute('echo $HOME')
        # TODO: handle self._remote_home_dir == None
        # create dir, in case it doesn't already exist
        self._host_data_dir = os.path.join(self._remote_home_dir,
            "data/bluesky/", self._run_id)
        await self._execute("mkdir -p {}".format(self._host_data_dir))
        # clear out any old output, if there is any
        await self._execute("rm -r {}".format(
            os.path.join(self._host_data_dir, '*')), ignore_errors=True)

    async def _write_remote_files(self):
        logging.info("Writing remote files on %s", self._ip)
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
        logging.info("Installing bluesky and dependencies on %s", self._ip)
        # Note: it's advised to have these pre-installed on the
        #    ec2 instance, but this is just in case they're not

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

        await self._execute("docker pull pnwairfire/bluesky:{}".format(
            self._config('bluesky_version')))

    async def _run_bluesky(self):
        """Runs bluesky

        Due to a bug in paramiko which causes it to hang on longer
        running processes, we run bsp in the background and then
        poll until it finishes.
        """
        logging.info("Running bluesky on %s", self._ip)
        cmd = self._form_bsp_command()
        # TODO: verify that ignore_errors=True is no longer needed now
        #   that we're running bsp in the background, and
        # Note: Running bsp through hysplit dispersion results in output
        #   to stderr even if run succeeds, e.g.
        #     'Warning 1: No UNIDATA NC_GLOBAL:Conventions attribute'
        #   So, ignore stderr
        await self._execute(cmd, ignore_errors=True)
        await self._wait_for_bsp_to_complete()
        await self._execute('sudo chown -R $USER:$USER {}'.format(
            self._host_data_dir))

    def _form_bsp_command(self):
        cmd = "docker run --name {name} -d --rm -v {host_data_dir}:/data/bluesky/".format(
            name=self._request_id, host_data_dir=self._host_data_dir)


        for v in self._config('aws', 'ec2', 'efs_volumes'):
            cmd += " -v {d}:{d}".format(d=v[1])

        cmd += (" pnwairfire/bluesky:{version}"
            " bsp --log-level=DEBUG"
            " --run-id={run_id}"
            " -c /data/bluesky/config.json"
            " -i /data/bluesky/input.json"
            " -o /data/bluesky/output.json"
            " --log-file /data/bluesky/output.log"
            " --today {today}"
            " {modules}"
            ).format(
                version=self._config('bluesky_version'),
                run_id=self._run_id,
                today=self._bluesky_today_str,
                modules=' '.join(self._config('bluesky', 'modules') + ['export'])
            )

        return cmd

    # TODO: make this configurable?
    BSP_POLL_WAIT = 30 # seconds

    async def _wait_for_bsp_to_complete(self):
        ps_cmd = 'docker ps -f name={} |grep -v CONTAINER'.format(self._request_id)
        while True:
            logging.info("Waiting %s before checking if bsp completed",
                self.BSP_POLL_WAIT)
            await asyncio.sleep(self.BSP_POLL_WAIT)
            try:
                await self._execute(ps_cmd)
            except Exception as e:
                # bsp must no longer be running
                # TODO: check output.log to make sure it completed?
                break
        logging.info("bsp run complete")

    async def _tarball(self):
        logging.info("Creating tarball on %s", self._ip)
        await self._execute(("cd {host_data_dir}/exports/; tar czf "
            " {run_id}.tar.gz {run_id}").format(
            host_data_dir=self._host_data_dir, run_id=self._run_id))

    async def _upload_aws_credentials(self):
        logging.info("Uploading AWS credentials to %s", self._ip)
        # Credentials are uploaded in order to push to s3
        remote_aws_dir = os.path.join(self._remote_home_dir, ".aws")
        if not await self._execute('ls {}'.format(remote_aws_dir)):
            local_aws_dir = os.path.join(os.environ["HOME"], ".aws/")
            # TODO: if recursive put fails, update put/get to support it
            await self._ssh_client.put(local_aws_dir, remote_aws_dir)

    async def _publish_output(self):
        logging.info("Publishing output from %s", self._ip)
        filename = "{}.tar.gz".format(self._run_id)
        s3_path = self._config('aws', 's3', 'output_path')
        await self._publish(filename, s3_path, '_output_url', 'exports/', '.tar.gz')

    async def _publish_log(self):
        logging.info("Publishing bluesky log file from %s", self._ip)
        await self._publish('output.log', 'log', '_log_url', '', '.log')

    EXT_EXTRACTOR = re.compile('\.([^.]+)')

    async def _publish(self, filename, s3_path, attr, local_path, ext):
        # os.path.joins handle's empty string local_path
        local_pathname = os.path.join(
            self._host_data_dir, local_path, filename)

        s3_path = s3_path.strip('/')
        bucket = self._config('aws', 's3', 'bucket_name')

        s3_filename = self._run_id + ext
        s3_url = "s3://" + os.path.join(
            bucket, s3_path, self._request_id, s3_filename)

        cmd = "aws s3 cp {} {}".format(local_pathname, s3_url)
        await self._execute(cmd)

        try:
            await self._execute("aws s3 ls {}".format(s3_url))
            setattr(self, attr, self._s3_url(s3_path, filename))
        except:
            # else attr remains None
            pass

    async def _cleanup(self):
        if self._config('cleanup_output'):
            logging.info("Cleaning up output on %s", self._ip)
            # delete the entire output dir
            await self._execute("rm -r {}".format(self._host_data_dir))


    REGION = "us-west-2" # TODO: don't hard code this

    def _s3_url(self, path, filename):
         return ("https://{bucket}.s3-{region}.amazonaws.com/{path}/"
            "{request_id}/{filename}").format(
                bucket=self._config('aws', 's3', 'bucket_name'),
                region=self.REGION, path=path.strip('/'),
                request_id=self._request_id, filename=filename)


    PARSE_ERROR_SCRIPT = """
        import json; import sys;
        output=json.loads(sys.stdin.read());
        error=output.get("failed_fires") and output["failed_fires"][0].get("error");
        sys.stdout.write(json.dumps(error or ""))
    """.replace("\n", "").strip()

    async def _check_output_for_error(self):
        # look in bluesky output for error, and return it
        cmd = "cat {}/output.json |python3 -c '{}'".format(
            self._host_data_dir, self.PARSE_ERROR_SCRIPT)
        d = await self._execute(cmd, ignore_errors=True)
        d = json.loads(d) if d else None
        return d