import json
import os
from collections import defaultdict

from afaws.asyncutils import run_in_loop_executor

__all__ = [
    "Status",
    "SystemErrors",
    "StatusTracker"
]

class Status(object):
    """Encapsulates string constants representing system and run statues"""

    # Used only for systemn stats
    COMPLETE = 'complete'

    # Used for both system and run statues
    WAITING = 'waiting'
    RUNNING = 'running'

    # Used only for run status
    SUCCESS = 'success'
    FAILURE = 'failure'
    UNKNOWN = "unknown"

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

class StatusTracker(object):

    def __init__(self, request_id, s3_client, config):
        self._s3_client = s3_client
        self._request_id = request_id
        self._config = config
        self._status = None

    async def _save_status(self):
        await run_in_loop_executor(self._s3_client.put_object,
            Body=json.dumps(self._status),
            Bucket=self._config('aws', 's3', 'bucket_name'),
            Key=os.path.join('status', self._request_id + '-status.json'))

    async def initialize(self):
        self._status = {
            "system_status": Status.RUNNING,
            "system_error": None,
            "counts": {
                Status.WAITING: 0,
                Status.RUNNING: 0,
                Status.SUCCESS: 0,
                Status.FAILURE: 0,
                Status.UNKNOWN: 0,
                Status.COMPLETE: 0
            },
            "runs": defaultdict(lambda: {})
        }
        await self._save_status()

    async def set_system_status(self, system_status, system_error=None):
        self._status['system_status'] = system_status
        if system_error:
            self._status['system_status'] = system_status

        await self._save_status()

    async def set_run_status(self, run, status, **kwargs):
        if self._status is None:
            await self.initialize()

        # Update run's status
        self._status["runs"][run._run_id]["status"] = status
        self._status["runs"][run._run_id].update(**kwargs)

        # Update count for this status, if it has a count
        if status in self._status['counts']:
            self._status['counts'][status] += 1

        # update running and complete counts, if appropriate
        if status in (Status.SUCCESS, Status.FAILURE, Status.UNKNOWN):
            self._status['counts'][Status.RUNNING] -= 1
            self._status['counts'][Status.COMPLETE] += 1

        await self._save_status()
