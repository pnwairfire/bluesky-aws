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

Under `bluesky-aws-admin` is a example configuration file,
`next.config.js.example`, that needs to be copied to `next.config.js`
and then modified to reflect your S3 bucket name, etc.

    cp bluesky-aws-admin/next.config.js.example bluesky-aws-admin/next.config.js
    # modify bluesky-aws-admin/next.config.js


## Build and Run

In a terminal:

    docker build -t bluesky-aws-admin . -f Dockerfile-admin
    docker run --rm -p 3000:3000 bluesky-aws-admin


In a browser, load http://localhost:3000/
