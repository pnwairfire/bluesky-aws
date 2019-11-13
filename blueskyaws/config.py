import copy
import logging

class MissingConfigurationError(Exception):
    pass

class InvalidConfigurationError(Exception):
    pass

class InvalidConfigurationUsageError(Exception):
    pass

class Config(object):

    _DEFAULTS = {
        "ec2_image_name": None,
        "ec2_instance_type": None,
        "s3_bucket_name": None,
        "modules": None,
        "bluesky_config_file": None,
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
                if isinstance(v, dict):
                    _(defaults[k], v, *new_parent_keys)
                else:
                    defaults[k] = v

        _(self._config, user_config)

    REQUIRED_CONFIG_KEYS = (
        'ec2_image_name', 'ec2_instance_type', 's3_bucket_name', "modules"
    )
    MISSING_CONFIG_FIELD_MSG = "BlueskyRunner config must define {}"

    def _check(self):
        for k in (self.REQUIRED_CONFIG_KEYS):
            if self._config.get(k) is None:
                raise MissingConfigurationError(
                    self.MISSING_CONFIG_FIELD_MSG.format(k))

    def _log(self):
        def _(config, *keys):
            for k, v in self._config:
                keys = keys + [k]
                if isinstance(v, dict):
                    _(v, *keys)
                else:
                    logging.debug("Config setting: %s: %s",
                        ' < '.join(keys, v))

    def __call__(self, *args):
        keys = list(args)
        val = self._config
        while keys:
            if not isinstance(val, dict):
                raise InvalidConfigurationUsageError()
            val = val[keys.pop(0)]
        return val
    get = __call__
