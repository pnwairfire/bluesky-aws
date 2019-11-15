# Configuration

## Required Configuration ettings

 - `aws` > `iam_instance_profile` > `Arn` --
 - `aws` > `iam_instance_profile` > `Name` --
 - `aws` > `ec2` > `image_id` -- name of image to luanch ec2 image
 - `aws` > `ec2` > `instance_type` -- instance type to use
 - `aws` > `ec2` > `key_pair_name` -- key pair to use for ssh
 - `aws` > `ec2` > `security_groups` -- security group that allows ssh access
 - `aws` > `s3` > `bucket_name` -- name of s3 bucket used for publishing output
 - `bluesky` > `modules` -- list of bluesky modules to run

## Optional Settings
 - `aws` > `ec2` > `efs_volumes` -- key pair to use for ssh
 - `bluesky` > `config_file` -- bluesky config file(s) to use when running bluesky; may be string or array (for specifying multiple files)
 - `notitifications` > `email` > `enabled` -- defaults to `false`
 - `notitifications` > `email` > `recipients` --
 - `notitifications` > `email` > `sender` -- defaults to 'blueskyaws@blueskyaws'
 - `notitifications` > `email` > `subject` --  defaults to 'BlueSky AWS Output Status'
 - `notitifications` > `email` > `smtp_server` --  defaults to 'localhost'
 - `notitifications` > `email` > `smtp_port` --  defaults to 1025
 - `notitifications` > `email` > `smtp_starttls` --  defaults to 'false'
 - `notitifications` > `email` > `username` --
 - `notitifications` > `email` > `password` --
