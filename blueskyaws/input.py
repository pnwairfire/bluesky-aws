import json
import math
import os
import rfc3987
import tempfile
import urllib

from .status import Status, SystemErrors

class InputLoadFailure(Exception):
    pass

class InputLoader(object):

    def __init__(self, input_file_name, status_tracker):
        """Loads data from input file

        Args:

         - input_file_name` - local file path name or url
        """
        self._orig_input_file_name = input_file_name
        self._status_tracker = status_tracker

    async def __aenter__(self):
        try:
            uri_parts = rfc3987.parse(input_file_name, rule='IRI')
            # set local file name
            self._tmp_dir = tempfile.mkdtemp()
            self._input_file_name = os.path.join(self._tmp_dir,
                os.path.basename(uri_parts['path']))
            self._attempts = 0
            await self._download()

        except:
            # TODO: check for file existence, and support retry logic (configurable)
            self._input_file_name = input_file_name

        self._load_input()

    async def __aexit__(self, exc_type, exc_value, traceback):
        # TODO: delete self._tmp_dir
        pass

    ## Properties

    @property
    def input_file_name(self):
        return self._input_file_name

    @property
    def fires(self):
        return self._fires

    ## Helper

    def _is_url(self, input_file_name):
        # TODO: more r
        return input_file_name.startswith('http')

    async def _download(self):
        """Downloads remote input data, with optional retry logic
        """
        self._attempts += 1
        # TODO: catch 404 and support retry logic (configurable)
        # TODO: if retries remaining, set status to waiting; else
        #    set status to fail with message saying that
        # TODO: download asyncronously
        try:
            urllib.request.urlretrieve(input_file_name, self._input_file_name)
            return

        except HTTPError as e:
            if getattr(e, 'code', None) == 404:
                if self._attempts < self._config('input', 'wait', 'max_attempts'):
                    wait_time = self._config('input', 'wait', 'time')
                    if self._config('input', 'wait', 'strategy') == 'backoff':
                        # first wait will be the configured wait time,
                        # second wait will be 2 x the configured wait time,
                        # third wait will be 4 x the configured wait time, etc.
                        wait_time * math.pow(2, self._attempts - 1)
                    self._download()
                    return

            # TODO: set system status to failure and set error message
            #    to something based on e
            self._status_tracker.set_system_status(Status.WAITING,
                system_error=SystemErrors.WAITING_FOR_FIRES)

        except Exception as e:

    def _load_input(self):
        with open(self._input_file_name, 'r') as f:
            # reset point to beginning of file and load json data
            f.seek(0)
            self._fires = json.loads(f.read())['fires']
