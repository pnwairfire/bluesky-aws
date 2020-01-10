import copy
import logging
from collections import OrderedDict

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


class ConfigSetting(object):

    def __init__(self, default, help_string=None, validator=None, required=False):
        self._default = default
        self._help_string = help_string
        self._validator = validator
        self._required = required

    @property
    def default(self):
        return self._default

    @property
    def help_string(self):
        return self._help_string or "(n/a)"

    @property
    def required(self):
        return self._required


    INVALID_CONFIG_FIELD_MSG = "Invalid config setting {} = {}"
    REQUIRED_CONFIG_SETTING_IS_NONE_MSG = "Required config setting {} can't be None"

    def validate(self, val, *keys):
        if self._validator and not self._validator(val):
            raise InvalidConfigurationError(
                self.INVALID_CONFIG_FIELD_MSG.format(' > '.join(keys), val))

        if self._required and val is None:
            raise InvalidConfigurationError(
                self.REQUIRED_CONFIG_SETTING_IS_NONE_MSG.format(
                ' > '.join(keys)))

    MISSING_CONFIG_FIELD_MSG = "Missing required config setting {}"

    def get_default(self, *keys):
        if self._required and self._default is None:
            raise MissingConfigurationError(
                self.MISSING_CONFIG_FIELD_MSG.format(' > '.join(keys)))

        return self._default


CONFIG_SETTINGS = OrderedDict({
    "request_id_format": ConfigSetting(None, help_string='\n'.join([
        "request_id_format is used in input, log, status, and output file names",
        "defaults to input file name with `.json` removed",
        "",
        "Supports the following wildcards:",
        " - '{uuid}' - replaced with an 8 character guid",
        " - '{utc_today}' - replaced with current UTC date, formatted '%Y%m%d'",
        " - '{utc_now}' - replaced with current UTC timestamp, formatted '%Y%m%dT%H%M%S'",
        "",
        "e.g. 'bluesky-aws-{uuid}-{utc_now}' would translate to something like",
        "'bluesky-aws-dk38fj3d-20191210T052322'"])
    ),

    "run_id_format": ConfigSetting(None, help_string='\n'.join([
        "run_id_format defaults to fire id.",
        "",
        "Supports the following wildcards:",
        " - '{request_id}' - replaced with the request id",
        " - '{uuid}' - replaced with an 8 character guid",
        " - '{fire_id}' - replaced with the id of the run's fire",
        " - '{utc_today}' - replaced with current UTC date, formatted '%Y%m%d'",
        " - '{utc_now}' - replaced with current UTC timestamp, formatted '%Y%m%dT%H%M%S'",
        "",
        "e.g. 'bluesky-aws-run-{fire_id}-{uuid}-{utc_today}' would translate",
        "to something like 'bluesky-aws-run-fire123-dk38fj3d-20191210'"])
    ),

    # bluesky_version must be astring value matching one of the published
    # bluesky docker image tags listed on
    # https://hub.docker.com/r/pnwairfire/bluesky/tags
    "bluesky_version": ConfigSetting("v4.1.31", help_string='\n'.join([
        "a string value matching one of the published bluesky docker image tags",
        "listed on https://hub.docker.com/r/pnwairfire/bluesky/tags"]),
        required=True),

    "input": {
        "wait": {
            "strategy": ConfigSetting("fixed", help_string="wait strategy",
                validator=lambda v: v in ('fixed', 'backoff')),
            "time": ConfigSetting(15*60, "wait time, in seconds"), # seconds
            "max_attempts": ConfigSetting(3, "max number to attempts before aborting")
        }
    },

    # setting cleanup_output to False is only useful when using an
    # existing instance in dev, when you might want to inspect
    # the output on the instance after the run
    "cleanup_output": ConfigSetting(True, help_string='\n'.join([
        "Whether or not to delete output after publihing to s3.",
        "",
        "Only useful when using an existing instance, when you might want to",
        "inspect the output on the instance after the run; defaults to `false`."])
    ),
    "ssh_key": ConfigSetting(None,help_string="""
        ssh key to use for ssh'ing to and running commands on ec2 instances
    """, required=True),

    "aws": {
        "iam_instance_profile": {
            "Arn": ConfigSetting(None, required=True),
            "Name": ConfigSetting(None, required=True)
        },
        "ec2": {
            "max_num_instances": ConfigSetting(None,
                help_string="the maximum number of new plus existing instances to use"),
            "image_name_prefix_format": ConfigSetting("bluesky-aws-{request_id}", help_string='\n'.join([
                "Prefix to use in name of each new instance",
                "",
                "A guid assigned to the request will be appended to the",
                "image_name_prefix_format to prevent name collisions.",
                "An integer from 1 to num_new_instances will then be appended",
                "to that. If image_name_prefix_format is set to null or",
                "an empty string, each image will be named simply with the guid",
                "plus the integer",
                "",
                "Supports the following wildcards:",
                " - '{request_id}' - replaced with the request id",
                "",
                "e.g. '{request_id}-', given request id 'bluesky-aws-20191210'",
                "would translate to something like 'bluesky-aws-20191210-sjdk1j23-2'"])
            ),
            "image_id": ConfigSetting(None, help_string="name of image to luanch ec2 image", required=True),
            "instance_type": ConfigSetting(None, help_string="instance type to use", required=True),
            "key_pair_name": ConfigSetting(None, help_string="key pair to use for ssh", required=True),
            "security_groups": ConfigSetting(None, help_string="security group that allows ssh access", required=True),
            "efs_volumes": ConfigSetting(None, help_string=""),
            "ebs": {
                "volume_size": ConfigSetting(8, help_string="EBS volume size (GB); default 8GB"),
                "device_name": ConfigSetting("/dev/sda1", help_string="EBS volume device name; default '/dev/sda1'") # TODO: default ot '/dev/xvda' ?
            }
        },
        "s3": {
            "bucket_name": ConfigSetting(None,
                help_string="name of s3 bucket used for publishing output",
                required=True),
            "output_path": ConfigSetting("output",
                help_string="output path to nest output under within s3 bucket; defaults to 'output'",
                required=True)
        }
    },
    "bluesky": {
        "today": ConfigSetting(None,
            help_string="'today' defaults to current day (i.e not specified in the pipeline command)"),
        "modules": ConfigSetting(None,
            help_string="list of bluesky modules to run", required=True),
        "config_file": ConfigSetting(None, help_string="""
            bluesky config file(s) to use when running bluesky;
            may be string or array (for specifying multiple files)
        """),
        "config": ConfigSetting({}, help_string="""
            bluesky config settings that override what's specified in the separate
            bluesky config file, if one is specified (see below)
        """),
    },
    "notifications": {
        "email": {
            'enabled': ConfigSetting(False, help_string="defaults to false",
                validator=lambda v: isinstance(v, bool)),
            'recipients': ConfigSetting([], help_string="",
                validator=lambda v: isinstance(v, list)),
            'sender': ConfigSetting('blueskyaws@blueskyaws', help_string="defaults to 'blueskyaws@blueskyaws'"),
            'subject': ConfigSetting('BlueSky AWS Output Status', help_string="defaults to 'BlueSky AWS Output Status'"),
            'smtp_server': ConfigSetting('localhost', help_string="defaults to 'localhost'"),
            'smtp_port': ConfigSetting(1025, help_string="defaults to 1025",
                validator=lambda v: isinstance(v, int)),
            'smtp_starttls': ConfigSetting(False, help_string="defaults to false",
                validator=lambda v: isinstance(v, bool)),
            'username': ConfigSetting(None, help_string=""),
            'password': ConfigSetting(None, help_string="")
        }
    }
})

class ConfigSettingsMarkdownGenerator(object):

    def __init__(self):
        self._required_text = ""
        self._optional_text = ""
        self._generate()

    @property
    def required(self):
        return self._required_text

    @property
    def optional(self):
        return self._optional_text


    CONFIG_SETTINGS_MARKDOWN_TEMPLATE = """### {keys}

default: {default}

{help_string}

"""

    def _generate(self):
        def _gen(config_settings, *parent_keys):
            for k, v in config_settings.items():
                new_parent_keys = list(parent_keys) + [k]
                if isinstance(config_settings[k], ConfigSetting):
                    text = self.CONFIG_SETTINGS_MARKDOWN_TEMPLATE.format(
                        keys=' > '.join(new_parent_keys),
                        default=config_settings[k].default,
                        help_string=config_settings[k].help_string.strip()
                    ).strip() +'\n\n'

                    # TODO: convert all '\n \w*' into just '\n'

                    if config_settings[k].required:
                        self._required_text += text
                    else:
                        self._optional_text += text

                elif isinstance(config_settings[k], dict):
                    _gen(config_settings[k], *new_parent_keys)

                # else leave is is - must be an already set config setting value

        _gen(CONFIG_SETTINGS)

class Config(object):

    def __init__(self, config):
        if hasattr(config, '_config'):
            self._config = copy.deepcopy(config._config)
        else:
            self._set(config)

        self._log()


    INVALID_CONFIG_FIELD_MSG = "Invalid config field {}"

    def _set(self, user_config):
        # Initialize config to config settings
        self._config = copy.deepcopy(CONFIG_SETTINGS)

        # Override values that are specified in the user config
        def _set(defaults, config, *parent_keys):
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

                if isinstance(defaults[k], ConfigSetting):
                    defaults[k].validate(v, *new_parent_keys)
                    defaults[k] = v

                else:
                    _set(defaults[k], v, *new_parent_keys)

        _set(self._config, user_config)


        # Fill in anything not specified in user config by converting
        def _fill(config, *parent_keys):
            for k, v in config.items():
                new_parent_keys = list(parent_keys) + [k]
                if isinstance(config[k], ConfigSetting):
                    # replace with default
                    config[k] = config[k].get_default(*new_parent_keys)

                elif isinstance(config[k], dict):
                    _fill(config[k], *new_parent_keys)

                # else leave is is - must be an already set config setting value

        _fill(self._config)


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
