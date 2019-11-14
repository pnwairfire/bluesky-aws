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
                # ec2_image_id should *not* be a dict
                "ec2_image_id": {'s': 13}
            })
        assert e_info.value.args[0] == Config.INVALID_CONFIG_FIELD_MSG.format(
            'ec2_image_id')

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
            'ec2_image_id')

    def test_user_config_missing_some_required(self):
        with raises(MissingConfigurationError) as e_info:
            Config({'ec2_image_id': 'sdf'})
        assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
            'ec2_instance_type')

    def test_user_config_has_undefined_required(self):
        with raises(MissingConfigurationError) as e_info:
            Config({
                'ec2_image_id': 'sdf',
                "ec2_instance_type": None,
                "s3_bucket_name": 'sdf',
                'modules': ['fuelbeds']
            })
        assert e_info.value.args[0] == Config.MISSING_CONFIG_FIELD_MSG.format(
            'ec2_instance_type')

    ## Valid

    def test_only_required(self):
        c = Config({
            'ec2_image_id': 'sdf',
            "ec2_instance_type": 's',
            "s3_bucket_name": 'd',
            'modules': ['fuelbeds']
        })
        expected = {
            'ec2_image_id': 'sdf',
            "ec2_instance_type": 's',
            "s3_bucket_name": 'd',
            'modules': ['fuelbeds'],
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
        assert c._config == expected

        assert c('ec2_image_id') == 'sdf'
        assert c.get('ec2_image_id') == 'sdf'

        assert c('notifications', 'email') == expected['notifications']['email']
        assert c.get('notifications', 'email') == expected['notifications']['email']

        assert c('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'
        assert c.get('notifications', 'email', 'sender') == 'blueskyaws@blueskyaws'

    def test_required_and_optional(self):
        c = Config({
            'ec2_image_id': 'sdf',
            "ec2_instance_type": 's',
            "s3_bucket_name": 'd',
            'modules': ['fuelbeds'],
            "notifications": {
                "email": {
                    'enabled': True,
                    'recipients': ['foo@bar.baz'],
                    'sender': 'foo@airfire.org'
                }
            }
        })
        expected = {
            'ec2_image_id': 'sdf',
            "ec2_instance_type": 's',
            "s3_bucket_name": 'd',
            'modules': ['fuelbeds'],
            "bluesky_config_file": None,
            "notifications": {
                "email": {
                    'enabled': True,
                    'recipients': ['foo@bar.baz'],
                    'sender': 'foo@airfire.org',
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

        assert c('ec2_image_id') == 'sdf'
        assert c.get('ec2_image_id') == 'sdf'

        assert c('notifications', 'email') == expected['notifications']['email']
        assert c.get('notifications', 'email') == expected['notifications']['email']

        assert c('notifications', 'email', 'sender') == 'foo@airfire.org'
        assert c.get('notifications', 'email', 'sender') == 'foo@airfire.org'
