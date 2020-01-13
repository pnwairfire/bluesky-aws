# Development

## Building Docker Image

Build the docker image:

    docker build -t bluesky-aws . \
        --build-arg UID=$(id -u) \
        --build-arg GID=$(id -g)


## Run

Copy aws credentials into .aws/ in the repo root dir
and run

    docker run --rm -ti --user blueskyaws \
        -v $PWD/:/bluesky-aws/ \
        -v $PWD/.aws/:/home/blueskyaws/.aws/ \
        -v $HOME/.ssh:/home/blueskyaws/.ssh \
        bluesky-aws \
        ./bin/run-bluesky    \
        --log-level DEBUG \
        -i ./dev/data/3-fires.json \
        -c ./dev/config/bluesky-aws/simple.json

### `awscli` utility

The `awscli` utility is helpful for managing the files published to S3.
The following examples assume bucket name `bluesky-aws` and
EC2 instance  `dev-ec2-instance`.

Check the contents of the aws bucket

    aws s3 ls s3://bluesky-aws/
    aws s3 ls s3://bluesky-aws/requests/
    aws s3 ls s3://bluesky-aws/status
    ...

Download files

    aws s3 cp s3://bluesky-aws-dev/status/emissions-status.json .

Clear out old data:

    aws s3 rm s3://bluesky-aws-dev/status/emissions-status.json
    aws s3 rm --recursive s3://bluesky-aws-dev/

### Dev Scripts

In addition to using the `aws s3 rm ...` command, you can delete old output
with the `clear-output` dev script:

    ./dev/scripts/clear-output -b bluesky-aws

To additionally delete output data on an ec2 instance, e.g.

    ./dev/scripts/clear-output -b bluesky-aws -i dev-ec2-instance


## iPython

    docker run --rm -ti --user blueskyaws \
        -v $PWD/:/bluesky-aws/ \
        -v $PWD/.aws/:/home/blueskyaws/.aws/ \
        -v $HOME/.ssh:/home/blueskyaws/.ssh \
        bluesky-aws \
        ipython


## Unit Tests

    docker run --rm -ti --user blueskyaws \
        -v $PWD/:/bluesky-aws/ \
        -v $PWD/.aws/:/home/blueskyaws/.aws/ \
        -v $HOME/.ssh:/home/blueskyaws/.ssh \
        bluesky-aws \
        py.test
