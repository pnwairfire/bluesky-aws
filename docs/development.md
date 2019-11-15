# Development

## Building Docker Image

Build the docker image:

    docker build -t bluesky-aws .\
        --build-arg UID=$(id -u) \
        --build-arg GID=$(id -g)

## Run

Copy aws credentials into .aws/ in the repo root dir
and run

    docker run --rm -ti --user blueskyaws \
        -v $PWD/:/bluesky-aws/ -v $PWD/.aws/:/root/.aws/ \
        -v $HOME/.ssh:/root/.ssh bluesky-aws \
        ./bin/run-dispersion --log-level DEBUG \
        -i ./dev/data/3-fires.json \
        -c ./dev/config/simple-config.json

## iPython

    docker run --rm -ti --user blueskyaws \
        -v $PWD/:/bluesky-aws/ -v $PWD/.aws/:/root/.aws/ \
        -v $HOME/.ssh:/root/.ssh bluesky-aws ipython

## Unit Tests

    docker run --rm -ti --user blueskyaws \
        -v $PWD/:/bluesky-aws/ -v $PWD/.aws/:/root/.aws/ \
        -v $HOME/.ssh:/root/.ssh bluesky-aws py.test
