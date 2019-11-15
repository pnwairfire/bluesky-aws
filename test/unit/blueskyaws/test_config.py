from py.test import raises

from blueskyaws.config import (
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
            Config({
                # notifications *should* be a dict
                "notifications": "sdf"
            })
        assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
            'notifications')

    ## Missing Required

    def test_empty_user_config(self):
        with raises(MissingConfigurationError) as e_info:
            Config({})
        assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
            'aws > iam_instance_profile > Arn')

    def test_user_config_missing_some_required(self):
        with raises(MissingConfigurationError) as e_info:
            Config({
                "aws": {
                    "iam_instance_profile": {
                        "Arn": "sdfsdf"
                    }
                }
            })
        assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
            'aws > iam_instance_profile > Name')

    def test_user_config_has_undefined_required(self):
        with raises(MissingConfigurationError) as e_info:
            Config({
                "aws": {
                    "iam_instance_profile": {
                        "Arn": "sdf",
                        "Name": "dsdsdf"
                    },
                    "ec2": {
                        "image_id": None,
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
            })
        assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
            'aws > ec2 > image_id')

    ## Valid

    def test_only_required(self):
        c = Config({
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
            "aws": {
                "iam_instance_profile": {
                    "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                    "Name": "bluesky-iam-role"
                },
                "ec2": {
                    "image_id": "ami-123abc",
                    "instance_type":"t2.nano",
                    "key_pair_name": "sdfsdf",
                    "security_groups": ["ssh"],
                    "efs_volumes": None,
                },
                "s3": {
                    "bucket_name": "bluesky-aws"
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

        assert c('aws', 's3') == {"bucket_name": "bluesky-aws"}
        assert c.get('aws', 's3') == {"bucket_name": "bluesky-aws"}

        assert c('bluesky', 'config_file') == None
        assert c.get('bluesky', 'config_file') == None

        assert c('notifications', 'email') == expected['notifications']['email']
        assert c.get('notifications', 'email') == expected['notifications']['email']

        assert c('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
        assert c.get('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'

    def test_required_and_optional(self):
        c = Config({
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
            "aws": {
                "iam_instance_profile": {
                    "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                    "Name": "bluesky-iam-role"
                },
                "ec2": {
                    "image_id": "ami-123abc",
                    "instance_type":"t2.nano",
                    "key_pair_name": "sdfsdf",
                    "security_groups": ["ssh"],
                    "efs_volumes": None,
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

        assert c('aws', 's3') == {"bucket_name": "bluesky-aws"}
        assert c.get('aws', 's3') == {"bucket_name": "bluesky-aws"}

        assert c('bluesky', 'config_file') == "sdsdf.json"
        assert c.get('bluesky', 'config_file') == "sdsdf.json"

        assert c('notifications', 'email') == expected['notifications']['email']
        assert c.get('notifications', 'email') == expected['notifications']['email']

        assert c('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
        assert c.get('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
