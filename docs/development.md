# Development

## Building Docker Image and Running

Build the docker image:

    docker build -t bluesky-aws .

Copy aws credentials into .aws/ in the repo root dir
and run

    docker run --rm -ti -v $PWD/:/bluesky-aws/ -v $PWD/.aws/:/root/.aws/ \
        -v $HOME/.ssh:/root/.ssh bluesky-aws \
        ./bin/run-dispersion --log-level DEBUG \
        -i ./dev/data/3-fires.json \
        -c ./dev/config/simple-config.json


## Unit Tests

    docker run --rm -ti -v $PWD/:/bluesky-aws/ -v $PWD/.aws/:/root/.aws/ \
        -v $HOME/.ssh:/root/.ssh bluesky-aws py.test
