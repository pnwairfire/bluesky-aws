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

update:
> git pull


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

restart_admin:
> ./reboot-admin --background \
	--yaml-file bluesky-aws-admin/docker-compose-$(ENV).yml

bounce: require_env update build_all restart_admin
