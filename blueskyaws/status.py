
__all__ = [
    "Status",
    "SystemErrors",
    "StatusRecorder"
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
    WAITING_FOR_MET = "waiting_for_met"
    WAITING_FOR_FIRES = "waiting_for_fires"
    WAITING_FOR_FIRES_AND_MET = "waiting_for_fires_and_met"

    # Cases where one or more runs failed or are in an unknown state
    SOME_RUNS_FAILED = "some_runs_failed"
    SOME_RUNS_UNKNOWN = "some_runs_unknown"
    SOME_RUNS_UNKNOWN_AND_FAILED = "some_runs_unknown_and_failed"

class StatusRecorder(object):

    pass