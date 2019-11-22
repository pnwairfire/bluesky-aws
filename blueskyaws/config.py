import copy
import logging

__all__ = [
    "Config",
    "BLUESKY_EXPORT_CONFIG",
    "MissingConfigurationError",
    "InvalidConfigurationError",
    "InvalidConfigurationUsageError"
]

class MissingConfigurationError(Exception):
    pass

class InvalidConfigurationError(Exception):
    pass

class InvalidConfigurationUsageError(Exception):
    pass

class Config(object):

    _DEFAULTS = {
        "request_id_format": None, # defaults to input file name
        "run_id_format": None, # defaults to fire id
        "bluesky_version": "v4.1.27",
        "ssh_key": None,
        "aws": {
            "iam_instance_profile": {
                "Arn": None,
                "Name": None
            },
            "ec2": {
                "max_num_instances": None,
                "image_id": None,
                "instance_type": None,
                "key_pair_name": None,
                "security_groups": None,
                "efs_volumes": None,
                "ebs": {
                    "volume_size": 8,
                    "device_name": None
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
            "modules": [
                "fuelbeds",
                "consumption",
                "emissions"
            ],
            "config_file": None
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

        # We need to check, in case we're instantiating from an object
        # with fewer required fields.  e.g. ParallelConfig(Config({}))
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
                if isinstance(v, dict):
                    _(defaults[k], v, *new_parent_keys)
                else:
                    defaults[k] = v

        _(self._config, user_config)

    # Derived classse define REQUIRED_CONFIG_SETTINGS
    REQUIRED_CONFIG_SETTINGS = []
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

class ParallelConfig(Config):

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

class SingleConfig(Config):

    REQUIRED_CONFIG_SETTINGS = [
        # top level keys need extra comma to make a tuple
        ("bluesky_version", ),
        ("ssh_key", ),
        ("aws", "iam_instance_profile", "Arn"),
        ("aws", "iam_instance_profile", "Name"),
        ("aws", "s3", "bucket_name"),
        ("aws", "s3", "output_path"),
        ("bluesky", "modules")
    ]


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
