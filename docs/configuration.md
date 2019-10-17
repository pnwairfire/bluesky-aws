# Configuration

## Required Configuration ettings

 - `ec2_image_name` -- name of image to luanch ec2 image
 - `ec2_instance_type` -- instance type to use
 - `s3_bucket_name` -- name of s3 bucket used for publishing output

## Optional Settings
 - `bluesky_config_file` -- bluesky config file(s) to use when running bluesky; may be string or array (for specifying multiple files)
 - `notitifications` > `email` > `enabled` -- defaults to `false`
 - `notitifications` > `email` > `recipients` --
 - `notitifications` > `email` > `sender` -- defaults to 'blueskyaws@blueskyaws'
 - `notitifications` > `email` > `subject` --  defaults to 'BlueSky AWS Output Status'
 - `notitifications` > `email` > `smtp_server` --  defaults to 'localhost'
 - `notitifications` > `email` > `smtp_port` --  defaults to 1025
 - `notitifications` > `email` > `smtp_starttls` --  defaults to 'false'
 - `notitifications` > `email` > `username` --
 - `notitifications` > `email` > `password` --
