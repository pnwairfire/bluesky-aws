# bluesky-web Admin Web Dashboard

This web app is built with nextjs and reactjs.


## AWS configuraton

First, make sure you have the following two files, with values set
appropriately.

`~/.aws/config`

    [default]
    region=us-west-2

`~/.aws/credentials`

    [default]
    aws_access_key_id = __KEY__
    aws_secret_access_key = __SECRET__

See https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html for more information


## NextJS configuration

Under `bluesky-aws-admin` is an example configuration file,
`next.config.js.example`, that needs to be copied to `next.config.js`
and then modified to reflect your S3 bucket name, etc.

    cp bluesky-aws-admin/next.config.js.example bluesky-aws-admin/next.config.js
    # modify bluesky-aws-admin/next.config.js


## Build and Run

To run the development server, with source code mounted, use the
collowing command in a terminal:

    ENV=dev make bounce

In a browser, load http://localhost:3000/

In production:

    ENV=prod make update_to_latest_tag_and_bounce

## Running in Production with Custom Path Prefix

If you want to run in production with a custom path prefix, e.g. `/foo`,
you'll first need to update `next.config.js` to set `basePath` to `foo/`.
Then, you'll need to update the nginx config to set up a reverse proxy.
...FILL IN DETAILS...