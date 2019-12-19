import copy
import logging

__all__ = [
    "Config",
    "BLUESKY_EXPORT_CONFIG",
    "MissingConfigurationError",
    "InvalidConfigurationError",
    "InvalidConfigurationUsageError"
    "substitude_config_wildcards"
]

class MissingConfigurationError(Exception):
    pass

class InvalidConfigurationError(Exception):
    pass

class InvalidConfigurationUsageError(Exception):
    pass


def substitude_config_wildcards(config, *config_keys, **wildcard_dict):
    try:
        return (config(*config_keys) or '').format(**wildcard_dict)
    except KeyError as e:
        raise InvalidConfigurationError("Invalid wildcard, '{}', used in '{}' "
            "config field".format(e.args[0], config_key))


class Config(object):

    _DEFAULTS = {
        # request_id_format is used in input, log, status, and output file names
        # defaults to input file name with `.json` removed
        # Supports the following wildcards:
        #  '{uuid}' - replaced with an 8 character guid
        #  '{utc_today}' - replaced with current UTC date, formatted "%Y%m%d"
        #  '{utc_now}' - replaced with current UTC timestamp, formatted "%Y%m%dT%H%M%S"
        # e.g. "bluesky-aws-{uuid}-{utc_now}" would translate to something like
        # "bluesky-aws-dk38fj3d-20191210T052322"
        "request_id_format": None,

        # run_id_format defaults to fire id.
        # Supports the following wildcards:
        #  '{request_id}' - replaced with the request id
        #  '{uuid}' - replaced with an 8 character guid
        #  '{fire_id}' - replaced with the id of the run's fire
        #  '{utc_today}' - replaced with current UTC date, formatted "%Y%m%d"
        #  '{utc_now}' - replaced with current UTC timestamp, formatted "%Y%m%dT%H%M%S"
        # e.g. "bluesky-aws-run-{fire_id}-{uuid}-{utc_today}" would translate
        # to something like "bluesky-aws-run-fire123-dk38fj3d-20191210"
        "run_id_format": None,

        # bluesky_version must be astring value matching one of the published
        # bluesky docker image tags listed on
        # https://hub.docker.com/r/pnwairfire/bluesky/tags
        "bluesky_version": "v4.1.31",

        "input": {
            "wait": {
                "strategy": "fixed", # alternatively, 'backoff'
                "time": 15*60, # seconds
                "max_attempts": 3
            }
        },

        # setting cleanup_output to False is only useful when using an
        # existing instance in dev, when you might want to inspect
        # the output on the instance after the run
        "cleanup_output": True,
        "ssh_key": None,
        "aws": {
            "iam_instance_profile": {
                "Arn": None,
                "Name": None
            },
            "ec2": {
                "max_num_instances": None,
                # A guid assigned to the request will be appended to the
                # image_name_prefix_format to prevent name collisions.
                # An integer from 1 to num_new_instances will then be appended
                # to that. If image_name_prefix_format is set to null or
                # an empty string, each image will be named simply with the guid
                # plus the integer
                # Supports the following wildcards:
                #  '{request_id}' - replaced with the request id
                # e.g. "{request_id}-", given request id "bluesky-aws-20191210"
                # would translate to something like "bluesky-aws-20191210-sjdk1j23-2"
                "image_name_prefix_format": "bluesky-aws-{request_id}",
                "image_id": None,
                "instance_type": None,
                "key_pair_name": None,
                "security_groups": None,
                "efs_volumes": None,
                "ebs": {
                    "volume_size": 8,
                    "device_name": "/dev/sda1" # TODO: default ot '/dev/xvda' ?
                }
            },
            "s3": {
                "bucket_name": None,
                "output_path": "output"
            }
        },
        "bluesky": {
            # 'today' defaults to current day (i.e not
            #  specified in the pipeline command)
            "today": None,
            "modules": None,
            "config_file": None,
            # config overrides to apply over what's loaded from config file
            "config": {}
        },
        "notifications": {
            "email": {
                'enabled': False,
                'recipients': [],
                'sender': 'blueskyaws@blueskyaws',
                'subject': 'BlueSky AWS Output Status',
                'smtp_server': 'localhost',
                'smtp_port': 1025,
                'smtp_starttls': False,
                'username': None,
                'password': None
            }
        }
    }

    def __init__(self, config):
        if hasattr(config, '_config'):
            self._config = copy.deepcopy(config._config)
        else:
            self._set(config)

        self._check()
        self._log()

    INVALID_CONFIG_FIELD_MSG = "Invalid config setting {}"

    def _set(self, user_config):
        self._config = copy.deepcopy(self._DEFAULTS)
        def _(defaults, config, *parent_keys):
            invalid_keys = set(config.keys()).difference(defaults.keys())
            if invalid_keys:
                raise InvalidConfigurationError(
                    self.INVALID_CONFIG_FIELD_MSG.format(
                        ' > '.join(list(parent_keys)
                        + [', '.join(sorted(invalid_keys))]))
                )

            for k, v in config.items():
                new_parent_keys = list(parent_keys) + [k]
                if isinstance(v, dict) != isinstance(defaults[k], dict):
                    raise InvalidConfigurationError(
                        self.INVALID_CONFIG_FIELD_MSG.format(
                        ' > '.join(new_parent_keys)))

                if isinstance(v, dict) and new_parent_keys != ['bluesky', 'config']:
                    _(defaults[k], v, *new_parent_keys)
                else:
                    defaults[k] = v

        _(self._config, user_config)

    REQUIRED_CONFIG_SETTINGS = [
        # top level keys need extra comma to make a tuple
        ("bluesky_version", ),
        ("ssh_key", ),
        ("aws", "iam_instance_profile", "Arn"),
        ("aws", "iam_instance_profile", "Name"),
        ("aws", "ec2", "image_id"),
        ("aws", "ec2", "instance_type"),
        ("aws", "ec2", "key_pair_name"),
        ("aws", "ec2", "security_groups"),
        ("aws", "s3", "bucket_name"),
        ("aws", "s3", "output_path"),
        ("bluesky", "modules")
    ]
    MISSING_CONFIG_FIELD_MSG = "BlueskyParallelRunner config must define {}"

    def _check(self):
        for keys in (self.REQUIRED_CONFIG_SETTINGS):
            if self._get_config_value(keys) is None:
                raise MissingConfigurationError(
                    self.MISSING_CONFIG_FIELD_MSG.format(' > '.join(keys)))

    def _log(self):
        def _(config, *keys):
            for k, v in self._config:
                keys = keys + [k]
                if isinstance(v, dict):
                    _(v, *keys)
                else:
                    logging.debug("Config setting: %s: %s",
                        ' < '.join(keys, v))

    def _get_config_value(self, args):
        keys = list(args)
        val = self._config
        while keys:
            if not isinstance(val, dict):
                raise InvalidConfigurationUsageError()
            val = val[keys.pop(0)]
        return val


    def __call__(self, *args):
        return self._get_config_value(args)
    get = __call__


BLUESKY_EXPORT_CONFIG = {
    "export": {
        "modes": ["localsave"],
        "extra_exports": ["dispersion", "visualization"],
        "localsave": {
            "handle_existing": "replace",
            "dest_dir": "/data/bluesky/exports/"
        }
    }
}
