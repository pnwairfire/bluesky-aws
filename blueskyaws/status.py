import json
import logging
import os
from collections import defaultdict

from afaws.asyncutils import run_in_loop_executor

__all__ = [
    "SystemState",
    "Status",
    "SystemErrors",
    "StatusTracker"
]

class SystemState(object):
    """Encapsulates string constants representing system state"""

    WAITING = 'waiting'
    RUNNING = 'running'
    COMPLETE = 'complete'

class SystemErrors(object):
    """Encapsulates string constants representing error states."""

    # Waiting for resources dependecies
    WAITING_FOR_FIRES = "waiting_for_fires"
    WAITING_FOR_MET = "waiting_for_met"
    # TODO: remove the folowing, since we're not concenred with met until
    #    we've already got the fires ???
    WAITING_FOR_FIRES_AND_MET = "waiting_for_fires_and_met"

    # Cases where one or more runs failed or are in an unknown state
    NO_FIRE_DATA = "no-fire-data"
    SOME_RUNS_FAILED = "some_runs_failed"
    SOME_RUNS_UNKNOWN = "some_runs_unknown"
    SOME_RUNS_UNKNOWN_AND_FAILED = "some_runs_unknown_and_failed"

class Status(object):
    """Encapsulates string constants representing run statues"""

    WAITING = 'waiting'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'
    UNKNOWN = "unknown"

class StatusTracker(object):

    def __init__(self, request_id, s3_client, config):
        self._s3_client = s3_client
        self._request_id = request_id
        self._config = config
        self._status = None

    async def _save_status(self):
        logging.info("Saving status %s", self._status)
        await run_in_loop_executor(self._s3_client.put_object,
            Body=json.dumps(self._status),
            Bucket=self._config('aws', 's3', 'bucket_name'),
            Key=os.path.join('status', self._request_id + '-status.json'))

    def _initialize_counts(self):
        self._status["counts"] = {
            Status.WAITING: 0,
            Status.RUNNING: 0,
            Status.SUCCESS: 0,
            Status.FAILURE: 0,
            Status.UNKNOWN: 0
        }

    async def initialize(self):
        logging.info("Initializing status tracker for %s", self._request_id)
        self._status = {
            "system_state": Status.RUNNING,
            "system_error": None,
            "system_message": None,
            "runs": defaultdict(lambda: {})
        }
        self._initialize_counts()
        await self._save_status()

    async def set_system_state(self, system_state, **kwargs):
        self._status['system_state'] = system_state
        self._status.update(**kwargs)

        await self._save_status()

    async def set_run_status(self, run, status, **kwargs):
        logging.info("Setting run status for %s", run.run_id)
        if self._status is None:
            await self.initialize()

        # Update run's status
        self._status["runs"][run.run_id]["status"] = status
        self._status["runs"][run.run_id].update(**kwargs)

        # update counts
        self._initialize_counts()
        for r in self._status["runs"].values():
            self._status["counts"][r['status']] += 1

        await self._save_status()
