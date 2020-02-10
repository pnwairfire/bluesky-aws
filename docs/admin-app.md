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
    docker run -d --rm  --name bluesky-aws-admin -p 3000:3000 \
        -v $HOME/.aws/:/root/.aws/ bluesky-aws-admin


In a browser, load http://localhost:3000/


## Run in Dev

This is to run with local files counted

    docker run --rm --name bluesky-aws-admin \
         -p 3000:3000 -v $HOME/.aws/:/root/.aws/ \
        -v $PWD/bluesky-aws-admin/components/:/bluesky-aws-admin/components/ \
        -v $PWD/bluesky-aws-admin/lib/:/bluesky-aws-admin/lib/ \
        -v $PWD/bluesky-aws-admin/pages/:/bluesky-aws-admin/pages/ \
        -v $PWD/bluesky-aws-admin/public/:/bluesky-aws-admin/public/ \
        -v $PWD/bluesky-aws-admin/next.config.js:/bluesky-aws-admin/next.config.js \
        bluesky-aws-admin npm run dev


## Running in Production with Custom Path Prefix

If you want to run in production with a custom path prefix, e.g. `/foo`,
you'll first need to update `next.config.js` to set `basePath` to `foo/`.
Then, you'll need to set up a reverse proxy. For example, using apache,
add the following to your apache config:

    ProxyPass /foo http://127.0.0.1:3000
    ProxyPassReverse /foo http://127.0.0.1:3000
