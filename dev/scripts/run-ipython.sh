#!/usr/bin/env bash

docker run --rm -ti --user blueskyaws \
    -v $PWD/:/bluesky-aws/ \
    -v $PWD/.aws/:/home/blueskyaws/.aws/ \
    -v $HOME/.ssh:/home/blueskyaws/.ssh \
    bluesky-aws \
    ipython

#    -v $HOME/code/pnwairfire-afaws/afaws/:/bluesky-aws/afaws/ \
