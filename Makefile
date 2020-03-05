.RECIPEPREFIX = >

build:
>   docker build -t bluesky-aws . \
        --build-arg UID=`id -u` \
        --build-arg GID=`id -g`
