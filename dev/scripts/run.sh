#!/usr/bin/env bash


SHOW_HELP=false
INPUT_FILE=false
BLUESKY_AWS_CONFIG_FILE=false
INSTANCE=false

while [ -n "$1" ]; do # while loop starts
    case "$1" in
    -h) SHOW_HELP=true && shift ;;
    -i) INPUT_FILE="$2" && shift && shift ;;
    -c) BLUESKY_AWS_CONFIG_FILE="$2" && shift && shift ;;
    --instance) INSTANCE="$2" && shift && shift ;;
    *) echo "Option $1 not recognized" && exit 1 ;;
    esac
done

if [ "$SHOW_HELP" = true ] ; then
    echo ""
    echo "Options:"
    echo "   -h          - show this help message"
    echo "   -i          - input data file"
    echo "   -c          - bluesky-aws config file"
    echo "   --instance  - Existing instance; optional"
    echo ""
    echo "Usage:"
    echo ""
    echo "   $0 -i ./dev/data/1-fire.json \\"
    echo "      -c ./dev-private/config/bluesky-aws/emissions.json"
    echo ""
    echo "   $0 -i ./dev/data/1-fire.json \\"
    echo "      -c ./dev-private/config/bluesky-aws/emissions.json \\"
    echo "      --instance bluesky-v4.1.29-test"
    echo ""
    exit 0
fi

if [ "$INPUT_FILE" = false ] || [ "$BLUESKY_AWS_CONFIG_FILE" = false ] ; then
    echo "*** ERROR: Specify '-i' and '-c' options. Use '-h' to see usage."
    exit 1
fi

echo "Options"
echo "  Input file: $INPUT_FILE"
echo "  BlueSky AWS config file: $BLUESKY_AWS_CONFIG_FILE"
echo "  Mode"

CMD="docker run --rm -ti --user blueskyaws \
-v $PWD/:/bluesky-aws/ \
-v $PWD/.aws/:/home/blueskyaws/.aws/ \
-v $HOME/.ssh:/home/blueskyaws/.ssh \
bluesky-aws \
./bin/run-bluesky \
--log-level INFO \
-i $INPUT_FILE \
-c $BLUESKY_AWS_CONFIG_FILE"

#    -v $HOME/code/pnwairfire-afaws/afaws/:/bluesky-aws/afaws/ \

if [ ! "$INSTANCE" = false ] ; then
    CMD="$CMD --instance $INSTANCE"
fi

echo "About to run:"
echo "   $CMD"

eval $CMD