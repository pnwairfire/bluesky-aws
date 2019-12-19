import json
import logging
import math
import os
import rfc3987
import tempfile
import time
import urllib

from afaws.asyncutils import run_in_loop_executor

from .status import Status, SystemErrors

class InputLoadFailure(Exception):
    pass

class InputLoader(object):

    def __init__(self, config, input_file_name, status_tracker):
        """Loads data from input file

        Args:

         - input_file_name` - local file path name or url of remote resource
        """
        self._config = config
        self._orig_input_file_name = input_file_name
        self._status_tracker = status_tracker

    async def __aenter__(self):
        try:
            uri_parts = rfc3987.parse(self._orig_input_file_name, rule='IRI')
            # set local file name
            self._tmp_dir = tempfile.mkdtemp()
            self._local_input_file_name = os.path.join(self._tmp_dir,
                os.path.basename(uri_parts['path']))
            self._attempts = 0
            await self._download(self._orig_input_file_name)

        except:
            # TODO: check for file existence, and support retry logic (configurable)
            self._local_input_file_name = self._orig_input_file_name

        await self._load_input()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # TODO: delete self._tmp_dir
        pass

    ## Properties

    @property
    def local_input_file_name(self):
        return self._local_input_file_name

    @property
    def fires(self):
        return self._fires

    ## Helper

    def _is_url(self, input_file_name):
        # TODO: more r
        return input_file_name.startswith('http')

    async def _download(self, remote_input_file_name):
        """Downloads remote input data, with optional retry logic
        """

        # catch 404's and retry
        @wait_to_retry(self._config, urllib.request.HTTPError,
            self._status_tracker, lambda e: getattr(e, 'code', None) == 404)
        async def _():
            await run_in_loop_executor(urllib.request.urlretrieve,
                remote_input_file_name, self._local_input_file_name)
            return
        await _()



        # TODO: if retries remaining, set status to waiting; else
        #    set status to fail with message saying that

            # TODO: set system status to failure and set error message
            #    to something based on e

    async def _load_input(self):
        @wait_to_retry(self._config, FileNotFoundError, self._status_tracker)
        async def _():
            with open(self._local_input_file_name, 'r') as f:
                # reset point to beginning of file and load json data
                f.seek(0)
                self._fires = json.loads(f.read())['fires']
        await _()


def wait_to_retry(config, exc_class, status_tracker, check_func=lambda e: True):

    def decorator(f):

        async def decorated(*args, **kwargs):
            wait_strategy = config('input', 'wait', 'strategy')
            wait_time = config('input', 'wait', 'time')
            max_attempts = config('input', 'wait', 'max_attempts')

            attempts = 1
            error_msg = "Fire data does not exist"
            while True:
                try:
                    return await f(*args, **kwargs)

                except exc_class as e:
                    if check_func(e) and attempts < max_attempts:
                        if wait_strategy == 'backoff':
                            # first wait will be the configured wait time,
                            # second wait will be 2 x the configured wait time,
                            # third wait will be 4 x the configured wait time, etc.
                            wait_time * math.pow(2, attempts - 1)

                        await status_tracker.set_system_status(Status.WAITING,
                            system_error=SystemErrors.WAITING_FOR_FIRES)
                        attempts += 1
                        logging.warn(("Waiting %s seconds before retrying "
                            "input load"), wait_time)
                        time.sleep(wait_time)
                    else:
                        break

                except Exception as e:
                    logging.warn("Failed to load input: %s", e)
                    error_msg = str(e)
                    break

            # We only get here if we reached the max number of retries
            # or if an exception unrelaterd to existence was caught
            logging.error("Failed to load input")
            await status_tracker.set_system_status(Status.FAILURE,
                system_error=SystemErrors.NO_FIRE_DATA,
                system_error_message=error_msg)
            raise InputLoadFailure(error_msg)

        return decorated

    return decorator
