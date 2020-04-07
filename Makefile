.RECIPEPREFIX = >
.DEFAULT_GOAL := print_help

# ifeq ($(ENV),)
# 	$(error Specify ENV - e.g. ENV=dev make ... )
# endif

print_help:
> echo && echo "Usage" && echo "\tENV=[dev|prod] make [build|...]" && echo \
	&& echo "Examples" && echo "\tmake build" && echo "\tENV=dev make build" \
	&& echo && echo "(note that ENV is not needed for all tasks)" && echo

require_env:
>	test -n "$(ENV)" || (echo && echo "*** ENV not specified - type 'make' for usage" && echo && exit 1)

# TODO: support alternate branch and/or remote
update:
> git pull origin master

update_to_latest_tag: update
> git checkout `git describe --abbrev=0 --tags`

build:
> docker build -t bluesky-aws . \
        --build-arg UID=`id -u` \
        --build-arg GID=`id -g`

clear_admin_cache:
> sudo rm -r bluesky-aws-admin/cache/* || echo "Cache already empty"

build_admin: require_env clear_admin_cache
> docker-compose -p bluesky-aws-admin \
	-f bluesky-aws-admin/docker-compose-$(ENV).yml build

build_all: require_env build build_admin

restart_admin: require_env
> ./reboot-admin --background \
	--yaml-file bluesky-aws-admin/docker-compose-$(ENV).yml

bounce: require_env update build_all restart_admin

bounce_to_latest_tag: require_env update_to_latest_tag build_all restart_admin
