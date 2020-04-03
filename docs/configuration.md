
<!--
    THIS FILE IS GENERATED. DO NOT MANUALLY EDIT.
    UPDATE ./dev/scripts/generate-config-doc INSTEAD
-->


# Configuration

Each bluesky-aws run is configured with a json file, with nested fields and
top level "config" key. A minimal config would look something like the
following:

```
{
    "config": {
        "ssh_key": "id_rsa",
        "aws": {
            "iam_instance_profile": {
                "Arn": "arn:aws:iam::abc123:instance-profile/bluesky-iam-role",
                "Name": "bluesky-iam-role"
            },
            "ec2": {
                "image_id": "ami-123abc",
                "instance_type":"t2.nano",
                "key_pair_name": "sdf",
                "security_groups": ["ssh"],
                "efs_volumes": [
                    ["fs-abc123.efs.us-west-2.amazonaws.com:/", "/Met/"]
                ]
            },
            "s3": {
                "bucket_name": "bluesky-aws"
            }
        },
        "bluesky": {
            "config_file": null,
            "modules": [
                "fuelbeds",
                "consumption",
                "emissions"
            ]
        }
    }
}
```

The full list of config settings is listed below.

## Required Configuration settings

Note that required settings with non-null default values don't need to be set
by the user.  They just can't be explicitly overridden by the user with a
null or otherwise invalid value.  For example, setting `bluesky_version`
can not be set to `null` or something like `foo`

#### bluesky_version

***default***: `v4.1.34`


a string value matching one of the published bluesky docker image tags
listed on https://hub.docker.com/r/pnwairfire/bluesky/tags

---

#### ssh_key

***default***: `None`

***example:*** `"/home/foo/.ssh/id_rsa.pem"`

absoulte path to ssh key file to use for ssh'ing to and running commands on ec2 instances

---

#### aws > iam_instance_profile > Arn

***default***: `None`

***example:*** `"arn:aws:iam::abc-123:instance-profile/bluesky-aws-role"`

(n/a)

---

#### aws > iam_instance_profile > Name

***default***: `None`

***example:*** `"bluesky-aws-role"`

(n/a)

---

#### aws > ec2 > image_id

***default***: `None`

***example:*** `"bluesky-v4.1.34-ubuntu"`

name of image to luanch ec2 image

---

#### aws > ec2 > instance_type

***default***: `None`

***example:*** `"t2.small"`

instance type to use

---

#### aws > ec2 > key_pair_name

***default***: `None`

***example:*** `"foo_id_rsa"`

Name of key pair in AWS to use for ssh

---

#### aws > ec2 > security_groups

***default***: `None`

***example:*** `["launch-wizard-1", "default"]`

security group that allows ssh access

---

#### aws > s3 > bucket_name

***default***: `None`

***example:*** `"bluesky-aws"`

name of s3 bucket used for publishing output

---

#### aws > s3 > output_path

***default***: `output`


output path to nest output under within s3 bucket; defaults to 'output'

---

#### bluesky > modules

***default***: `None`

***example:*** `["fuelbeds", "consumption", "emissions"]`

list of bluesky modules to run

---




## Optional Settings

#### request_id_format

***default***: `None`

***example:*** `"bluesky-aws-{input_file_name}"`

request_id_format is used in the status and request JSON file names,
and in the bluesky log and output tarball file names as well.
It defaults to the input file name with `.json` removed

Supports the following wildcards:
 - '{input_file_name}' - replaced with input file name, with `.json` removed
 - '{uuid}' - replaced with an 8 character guid
 - '{utc_today}' - replaced with current UTC date, formatted '%Y%m%d'
 - '{utc_now}' - replaced with current UTC timestamp, formatted '%Y%m%dT%H%M%S'

e.g. 'bluesky-aws-{uuid}-{utc_now}' would translate to something like
'bluesky-aws-dk38fj3d-20191210T052322'

---

#### run_id_format

***default***: `None`

***example:*** `"{request_id}-{fire_id}"`

run_id_format defaults to fire id.

Supports the following wildcards:
 - '{request_id}' - replaced with the request id
 - '{uuid}' - replaced with an 8 character guid
 - '{fire_id}' - replaced with the id of the run's fire
 - '{utc_today}' - replaced with current UTC date, formatted '%Y%m%d'
 - '{utc_now}' - replaced with current UTC timestamp, formatted '%Y%m%dT%H%M%S'
 - '{bluesky_today}' - replaced with bluesky's 'today' (defaulting to current
         UTC date, if 'today' isn't specified), formatted '%Y%m%d'

e.g. 'bluesky-aws-run-{fire_id}-{uuid}-{utc_today}' would translate
to something like 'bluesky-aws-run-fire123-dk38fj3d-20191210'
Note that standard strftime wildcards are also supported (e.g. '%Y-%m-%d'),
and are filled in with the current UTC timestamp

---

#### input > wait > strategy

***default***: `fixed`


wait strategy

---

#### input > wait > time

***default***: `900`


wait time, in seconds

---

#### input > wait > max_attempts

***default***: `3`


max number to attempts before aborting

---

#### cleanup_output

***default***: `True`


Whether or not to delete output after publihing to s3.

Only useful when using an existing instance, when you might want to
inspect the output on the instance after the run; defaults to `false`.

---

#### aws > ec2 > max_num_instances

***default***: `None`

***example:*** `50`

the maximum number of new plus existing instances to use

---

#### aws > ec2 > image_name_prefix_format

***default***: `bluesky-aws-{request_id}`


Prefix to use in name of each new instance

A guid assigned to the request will be appended to the
image_name_prefix_format to prevent name collisions.
An integer from 1 to num_new_instances will then be appended
to that. If image_name_prefix_format is set to null or
an empty string, each image will be named simply with the guid
plus the integer

Supports the following wildcards:
 - '{request_id}' - replaced with the request id

e.g. '{request_id}-', given request id 'bluesky-aws-20191210'
would translate to something like 'bluesky-aws-20191210-sjdk1j23-2'

---

#### aws > ec2 > efs_volumes

***default***: `None`

***example:*** `[["fs-abc123.efs.us-west-2.amazonaws.com:/", "/Met/"]]`

EFS volumes to mount. An array of arrays, formatted like:
```
"efs_volumes": [
    ["<hostname>:/", "/local/mount/path/"]
]
```

---

#### aws > ec2 > ebs > volume_size

***default***: `8`


EBS volume size (GB); default 8GB

---

#### aws > ec2 > ebs > device_name

***default***: `/dev/sda1`


EBS volume device name; default '/dev/sda1'

---

#### aws > ec2 > minutes_until_auto_shutdown

***default***: `None`

***example:*** `120`

Number of minutes to wait before instances shut themselves down; default: null (no auto-termination)

---

#### bluesky > today

***default***: `None`

***example:*** `"2020-03-01"`

'today' defaults to current day (i.e not specified in the pipeline command)

---

#### bluesky > config_file

***default***: `None`

***example:*** `"/dockerconainer/path/to/bluesky-config.json"`

bluesky config file(s) to use when running bluesky;
may be string or array (for specifying multiple files)

---

#### bluesky > config

***default***: `{}`


bluesky config settings that override what's specified in the separate
bluesky config file, if one is specified (see below)

---

#### bluesky > seconds_between_completion_checks

***default***: `30`


Seconds to wait between checking for run completion

---

#### notifications > email > enabled

***default***: `False`


defaults to false

---

#### notifications > email > recipients

***default***: `[]`


(n/a)

---

#### notifications > email > sender

***default***: `blueskyaws@blueskyaws`


defaults to 'blueskyaws@blueskyaws'

---

#### notifications > email > subject

***default***: `BlueSky AWS Output Status`


defaults to 'BlueSky AWS Output Status'

---

#### notifications > email > smtp_server

***default***: `localhost`


defaults to 'localhost'

---

#### notifications > email > smtp_port

***default***: `1025`


defaults to 1025

---

#### notifications > email > smtp_starttls

***default***: `False`


defaults to false

---

#### notifications > email > username

***default***: `None`

***example:*** `"joedoe"`

(n/a)

---

#### notifications > email > password

***default***: `None`

***example:*** `"123abc!"`

(n/a)

---




## BlueSky Configuration

The bluesky processes run by bluesky-aws may be configured in three
different ways, listed here in order of precedence

 1. On the `run-bluesky` command line with the options `-C`, `-B`, `-I`, `-F`, and `-J`
 2. In the `bluesky-aws` config file under `bluesky` > `config`
 3. in a separate `bluesky` config file, referenced in the `bluesky-aws` config by `bluesky` > `config_file`

For example, if the bluesky dispersion.num_hours is specified on the command line with

```
-I bluesky.config.dispersion.num_hours=24
```

in the `bluesky-aws` config file with


```
{
    "config": {
        ...,
        "bluesky": {
            ...,
            "config": {
                "dispersion": {
                    "num_hours": 48
                }
            }
        }
    }
}
```

And in the bluesky config file with:

```
{
    "config": {
        ...,
        "dispersion": {
            ...,
            "num_hours": 72
        }
    }
}
```

Then `num_hours` would be set to 24 for the bluesky run(s).
