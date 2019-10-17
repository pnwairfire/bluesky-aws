import logging

import boto3

from .config import Config

class DispersionRunner(object):

    def __init__(self, **config):
        self._config = Config(config)
        self._client = boto3.client('ec2')
        self._ec2 = boto3.resource('ec2')

    async def run(self, fire):
        logging.debug("Processing fire")
        await self._launch()
        await self._run()
        await self._publish()
        await self._terminate()
        # TODO: send notification; send email and/or post status to an API
        #   and/or something else.

    async def _launch(self):
        pass

    async def _run(self):
        pass

    async def _publish(self):
        pass

    async def _terminate(self):
        pass