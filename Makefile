.RECIPEPREFIX = >

build:
>   docker build -t bluesky-aws . \
        --build-arg UID=`id -u` \
        --build-arg GID=`id -g`

bounce_admin_production:
> git pull \
	&& ./reboot-admin --rebuild --background \
		--yaml-file bluesky-aws-admin/docker-compose-prod.yml
