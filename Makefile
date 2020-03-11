.RECIPEPREFIX = >

ifeq ($(ENV),)
  $(error ENV is not set)
endif

update:
> git pull

build:
> docker build -t bluesky-aws . \
        --build-arg UID=`id -u` \
        --build-arg GID=`id -g`

build_admin:
> docker-compose -p bluesky-aws-admin \
	-f bluesky-aws-admin/docker-compose-$(ENV).yml build

build_all: build build_admin

restart_admin:
> ./reboot-admin --background \
	--yaml-file bluesky-aws-admin/docker-compose-$(ENV).yml

bounce: update build_all restart_admin
