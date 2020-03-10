import copy

from py.test import raises

from blueskyaws.config import (
    ConfigSetting,
    Config,
    InvalidConfigurationError,
    InvalidConfigurationUsageError,
    MissingConfigurationError
)


class TestConfig(object):

    ## Invalid

    def test_invalid_key(self):
        with raises(InvalidConfigurationError) as e_info:
            Config({
                "sdfsdf": None
            })
        assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
            'sdfsdf')

    def test_invalid_keys(self):
        with raises(InvalidConfigurationError) as e_info:
            Config({
                "sdfsdf": None,
                "asd": 2131
            })
        assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
            'asd, sdfsdf')

    def test_invalid_nested_key(self):
        with raises(InvalidConfigurationError) as e_info:
            Config({
                "notifications": {
                    "email": {
                        "sdf": 324
                    }
                }
            })
        assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
            "notifications > email > sdf")

        with raises(InvalidConfigurationError) as e_info:
            Config({
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
        with raises(InvalidConfigurationError) as e_info:
            Config({
                "notifications": {
                    "fdfd": 123,
                    "dd": 2
                }
            })
        assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
            'notifications > dd, fdfd')

        with raises(InvalidConfigurationError) as e_info:
            Config({
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
        with raises(InvalidConfigurationError) as e_info:
            Config({
                "ssh_key": "id_rsa",
                "aws": "Sdfd",  # 'aws' should be a dict
                "bluesky": {"modules": ["fuelbeds"]}
            })
        assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
            'aws')

    ## Missing Required

    def test_empty_user_config(self):
        with raises(MissingConfigurationError) as e_info:
            Config({})
        assert e_info.value.args[0] == ConfigSetting.MISSING_CONFIG_FIELD_MSG.format(
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

        with raises(MissingConfigurationError) as e_info:
            Config(input_config)
        assert e_info.value.args[0] == ConfigSetting.MISSING_CONFIG_FIELD_MSG.format(
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

        with raises(InvalidConfigurationError) as e_info:
            Config(input_config)
        assert e_info.value.args[0] == (
            ConfigSetting.REQUIRED_CONFIG_SETTING_IS_NONE_MSG.format(
                'aws > iam_instance_profile > Name')
        )

    ## Valid

    def test_only_with_required_paralle_config(self):
        c = Config({
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
            "bluesky_version": "v4.1.34",
            'input': {
                'wait': {
                    'max_attempts': 3,
                    'strategy': 'fixed',
                    'time': 900
                }
            },
            "cleanup_output": True,
            "ssh_key": "id_rsa",
            "aws": {
                "iam_instance_profile": {
                    "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                    "Name": "bluesky-iam-role"
                },
                "ec2": {
                    "max_num_instances": None,
                    "image_name_prefix_format": "bluesky-aws-{request_id}",
                    "image_id": "ami-123abc",
                    "instance_type":"t2.nano",
                    "key_pair_name": "sdfsdf",
                    "security_groups": ["ssh"],
                    "efs_volumes": None,
                    "ebs": {
                        "volume_size": 8,
                        "device_name": "/dev/sda1"
                    },
                    "minutes_until_auto_shutdown": None
                },
                "s3": {
                    "bucket_name": "bluesky-aws",
                    "output_path": "output"
                }
            },
            "bluesky": {
                "today": None,
                "modules": [
                    "fuelbeds",
                    "consumption",
                    "emissions"
                ],
                "config_file": None,
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
        assert c._config == expected

        assert c('aws', 'ec2', 'image_id') == 'ami-123abc'
        assert c.get('aws', 'ec2', 'image_id') == 'ami-123abc'

        assert c('aws', 's3') == {
            "bucket_name": "bluesky-aws",
            "output_path": "output"
        }
        assert c.get('aws', 's3') == {
            "bucket_name": "bluesky-aws",
            "output_path": "output"
        }

        assert c('bluesky', 'config_file') == None
        assert c.get('bluesky', 'config_file') == None

        assert c('notifications', 'email') == expected['notifications']['email']
        assert c.get('notifications', 'email') == expected['notifications']['email']

        assert c('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
        assert c.get('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'

    def test_required_and_optional(self):
        c = Config({
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
            "bluesky_version": "v4.1.34",
            'input': {
                'wait': {
                    'max_attempts': 3,
                    'strategy': 'fixed',
                    'time': 900
                }
            },
            "cleanup_output": True,
            "ssh_key": "id_rsa",
            "aws": {
                "iam_instance_profile": {
                    "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                    "Name": "bluesky-iam-role"
                },
                "ec2": {
                    "max_num_instances": None,
                    "image_name_prefix_format": "bluesky-aws-{request_id}",
                    "image_id": "ami-123abc",
                    "instance_type":"t2.nano",
                    "key_pair_name": "sdfsdf",
                    "security_groups": ["ssh"],
                    "efs_volumes": None,
                    "ebs": {
                        "volume_size": 8,
                        "device_name": "/dev/sda1"
                    },
                    "minutes_until_auto_shutdown": None
                },
                "s3": {
                    "bucket_name": "bluesky-aws",
                    "output_path": "output"
                }
            },
            "bluesky": {
                "today": None,
                "modules": [
                    "fuelbeds",
                    "consumption",
                    "emissions"
                ],
                "config_file": "sdsdf.json",
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
        assert c._config == expected

        assert c('aws', 'ec2', 'image_id') == 'ami-123abc'
        assert c.get('aws', 'ec2', 'image_id') == 'ami-123abc'

        assert c('aws', 's3') == {
            "bucket_name": "bluesky-aws",
            "output_path": "output"
        }
        assert c.get('aws', 's3') == {
            "bucket_name": "bluesky-aws",
            "output_path": "output"
        }

        assert c('bluesky', 'config_file') == "sdsdf.json"
        assert c.get('bluesky', 'config_file') == "sdsdf.json"

        assert c('notifications', 'email') == expected['notifications']['email']
        assert c.get('notifications', 'email') == expected['notifications']['email']

        assert c('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
        assert c.get('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
