import json
import os
import rfc3987
import tempfile
import urllib

class InputLoader(object):

    def __init__(self, input_file_name):
        """Loads data from input file

        Args:

         - input_file_name` - local file path name or url
        """
        self._orig_input_file_name = input_file_name

    async def __aenter__(self):
        try:
            uri_parts = rfc3987.parse(input_file_name, rule='IRI')
            # set local file name
            self._tmp_dir = tempfile.mkdtemp()
            self._input_file_name = os.path.join(self._tmp_dir,
                os.path.basename(uri_parts['path']))
            # TODO: catch 404 and support retry logic (configurable)
            # TODO: download asyncronously
            urllib.urlretrieve(input_file_name, self._input_file_name)

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

    def _load_input(self):
        with open(self._input_file_name, 'r') as f:
            # reset point to beginning of file and load json data
            f.seek(0)
            self._fires = json.loads(f.read())['fires']
