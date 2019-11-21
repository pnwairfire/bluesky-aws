import copy

from py.test import raises

from blueskyaws.config import (
    Config,
    ParallelConfig,
    SingleConfig,
    InvalidConfigurationError,
    InvalidConfigurationUsageError,
    MissingConfigurationError
)


class TestConfig(object):

    ## Invalid

    def test_invalid_key(self):
        for klass in (Config, ParallelConfig, SingleConfig):
            with raises(InvalidConfigurationError) as e_info:
                klass({
                    "sdfsdf": None
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                'sdfsdf')

    def test_invalid_keys(self):
        for klass in (Config, ParallelConfig, SingleConfig):
            with raises(InvalidConfigurationError) as e_info:
                klass({
                    "sdfsdf": None,
                    "asd": 2131
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                'asd, sdfsdf')

    def test_invalid_nested_key(self):
        for klass in (Config, ParallelConfig, SingleConfig):
            with raises(InvalidConfigurationError) as e_info:
                klass({
                    "notifications": {
                        "email": {
                            "sdf": 324
                        }
                    }
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                "notifications > email > sdf")

            with raises(InvalidConfigurationError) as e_info:
                klass({
                    "notifications": {
                        "ssdfdsf": 123132,
                        "email": {
                            "sdf": 324
                        }
                    }
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                "notifications > ssdfdsf")

    def test_invalid_nested_keys(self):
        for klass in (Config, ParallelConfig, SingleConfig):
            with raises(InvalidConfigurationError) as e_info:
                klass({
                    "notifications": {
                        "fdfd": 123,
                        "dd": 2
                    }
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                'notifications > dd, fdfd')

            with raises(InvalidConfigurationError) as e_info:
                klass({
                    "notifications": {
                        "email": {
                            "sdfsdf": None,
                            "asd": 2131
                        }
                    }
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                'notifications > email > asd, sdfsdf')

    def test_invalid_nesting(self):
        for klass in (Config, ParallelConfig, SingleConfig):
            with raises(InvalidConfigurationError) as e_info:
                klass({
                    "aws": {
                        "ec2": {
                            # image_id should *not* be a dict
                            "image_id": {'s': 13}
                        }
                    }
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                'aws > ec2 > image_id')

            with raises(InvalidConfigurationError) as e_info:
                klass({
                    # notifications *should* be a dict
                    "notifications": "sdf"
                })
            assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
                'notifications')

    ## Missing Required

    def test_empty_user_config(self):
        # empty Config is fine
        c = Config({})
        assert c._config == Config._DEFAULTS

        # Empty ParallelConfig and SingleConfig fail
        for klass in (ParallelConfig, SingleConfig):
            with raises(MissingConfigurationError) as e_info:
                klass({})
            assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
                'ssh_key')

    def test_user_config_missing_some_required(self):
        input_config = {
            "ssh_key": "id_rsa",
            "aws": {
                "iam_instance_profile": {
                    "Arn": "sdfsdf"
                }
            }
        }

        # Config has no required
        c = Config(input_config)
        expected = copy.deepcopy(Config._DEFAULTS)
        expected['ssh_key'] =  'id_rsa'
        expected['aws']['iam_instance_profile']['Arn'] = "sdfsdf"
        assert c._config == expected

        # Both Parallel and Single config require iam instance profile name
        for klass in (ParallelConfig, SingleConfig):
            with raises(MissingConfigurationError) as e_info:
                klass(input_config)
            assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
                'aws > iam_instance_profile > Name')

    def test_user_config_has_undefined_required(self):
        input_config = {
            "ssh_key": "id_rsa",
            "aws": {
                "iam_instance_profile": {
                    "Arn": "sdf",
                    "Name": None
                },
                "ec2": {
                    "image_id": "sdfds",
                    "instance_type": "t2.nano",
                    "key_pair_name": "sdfsdf",
                    "security_groups": ["ssh"],
                },
                "s3": {
                    "bucket_name": "foo",
                }
            },
            "bluesky": {
                "modules": [
                    "fuelbeds",
                    "consumption",
                    "emissions"
                ]
            }
        }

        # Config has no required
        c = Config(input_config)
        expected = dict(copy.deepcopy(Config._DEFAULTS), **input_config)
        expected['aws']['ec2']['max_num_instances'] = None
        expected['aws']['ec2']['efs_volumes'] = None
        expected['aws']['ec2']['ebs'] = {"volume_size": 8, "device_name": None}
        expected['aws']['s3']['output_path'] = "dispersion"
        expected['bluesky']['config_file'] = None
        assert c._config == expected

        # Both Parallel and Single config require iam instance profile name
        for klass in (ParallelConfig, SingleConfig):
            with raises(MissingConfigurationError) as e_info:
                klass(input_config)
            assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
                'aws > iam_instance_profile > Name')

    ## Valid

    def test_only_with_required_paralle_config(self):
        # This is miniumal set of config for ParallelConfig;
        # is superset of what's required by SingleConfig and
        # Config (which requires nothing)
        for klass in (Config, ParallelConfig, SingleConfig):
            c = klass({
                "ssh_key": "id_rsa",
                "aws": {
                    "iam_instance_profile": {
                        "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                        "Name": "bluesky-iam-role"
                    },
                    "ec2": {
                        "image_id": "ami-123abc",
                        "instance_type":"t2.nano",
                        "key_pair_name": "sdfsdf",
                        "security_groups": ["ssh"]
                    },
                    "s3": {
                        "bucket_name": "bluesky-aws",
                    }
                },
                "bluesky": {
                    "modules": [
                        "fuelbeds",
                        "consumption",
                        "emissions"
                    ]
                }
            })
            expected = {
                "request_id_format": None,
                "run_id_format": None,
                "bluesky_version": "v4.1.27",
                "ssh_key": "id_rsa",
                "aws": {
                    "iam_instance_profile": {
                        "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                        "Name": "bluesky-iam-role"
                    },
                    "ec2": {
                        "max_num_instances": None,
                        "image_id": "ami-123abc",
                        "instance_type":"t2.nano",
                        "key_pair_name": "sdfsdf",
                        "security_groups": ["ssh"],
                        "efs_volumes": None,
                        "ebs": {
                            "volume_size": 8,
                            "device_name": None
                        }
                    },
                    "s3": {
                        "bucket_name": "bluesky-aws",
                        "output_path": "dispersion"
                    }
                },
                "bluesky": {
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
            assert c._config == expected

            assert c('aws', 'ec2', 'image_id') == 'ami-123abc'
            assert c.get('aws', 'ec2', 'image_id') == 'ami-123abc'

            assert c('aws', 's3') == {
                "bucket_name": "bluesky-aws",
                "output_path": "dispersion"
            }
            assert c.get('aws', 's3') == {
                "bucket_name": "bluesky-aws",
                "output_path": "dispersion"
            }

            assert c('bluesky', 'config_file') == None
            assert c.get('bluesky', 'config_file') == None

            assert c('notifications', 'email') == expected['notifications']['email']
            assert c.get('notifications', 'email') == expected['notifications']['email']

            assert c('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
            assert c.get('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'

    def test_required_and_optional(self):
        for klass in (Config, ParallelConfig, SingleConfig):
            c = klass({
                "ssh_key": "id_rsa",
                "aws": {
                    "iam_instance_profile": {
                        "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                        "Name": "bluesky-iam-role"
                    },
                    "ec2": {
                        "image_id": "ami-123abc",
                        "instance_type":"t2.nano",
                        "key_pair_name": "sdfsdf",
                        "security_groups": ["ssh"]
                    },
                    "s3": {
                        "bucket_name": "bluesky-aws",
                    }
                },
                "bluesky": {
                    "modules": [
                        "fuelbeds",
                        "consumption",
                        "emissions"
                    ],
                    "config_file": "sdsdf.json"  # optional
                }
            })
            expected = {
                "request_id_format": None,
                "run_id_format": None,
                "bluesky_version": "v4.1.27",
                "ssh_key": "id_rsa",
                "aws": {
                    "iam_instance_profile": {
                        "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                        "Name": "bluesky-iam-role"
                    },
                    "ec2": {
                        "max_num_instances": None,
                        "image_id": "ami-123abc",
                        "instance_type":"t2.nano",
                        "key_pair_name": "sdfsdf",
                        "security_groups": ["ssh"],
                        "efs_volumes": None,
                        "ebs": {
                            "volume_size": 8,
                            "device_name": None
                        }
                    },
                    "s3": {
                        "bucket_name": "bluesky-aws",
                        "output_path": "dispersion"
                    }
                },
                "bluesky": {
                    "modules": [
                        "fuelbeds",
                        "consumption",
                        "emissions"
                    ],
                    "config_file": "sdsdf.json"
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
            assert c._config == expected

            assert c('aws', 'ec2', 'image_id') == 'ami-123abc'
            assert c.get('aws', 'ec2', 'image_id') == 'ami-123abc'

            assert c('aws', 's3') == {
                "bucket_name": "bluesky-aws",
                "output_path": "dispersion"
            }
            assert c.get('aws', 's3') == {
                "bucket_name": "bluesky-aws",
                "output_path": "dispersion"
            }

            assert c('bluesky', 'config_file') == "sdsdf.json"
            assert c.get('bluesky', 'config_file') == "sdsdf.json"

            assert c('notifications', 'email') == expected['notifications']['email']
            assert c.get('notifications', 'email') == expected['notifications']['email']

            assert c('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
            assert c.get('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'

    # TODO: add tests for instantiating one *Config object from another