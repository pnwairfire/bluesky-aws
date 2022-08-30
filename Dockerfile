FROM python:3.9.13-alpine3.16

RUN apk add --update bash less vim curl

RUN pip install --upgrade pip

# The following build tools are for paramiko
RUN apk --update add --no-cache --virtual .build-deps \
        make automake gcc g++ \
    && apk --update add --no-cache \
        musl-dev libffi-dev openssl-dev python3-dev

# Note: afconfig is used by bluesky-aws, but it doesn't need
# to be explicitly listed in the following pip install package
# list, since it's installed as a dependency of afscripting
RUN pip install --extra-index https://pypi.airfire.org/simple \
    paramiko==2.4.2 \
    boto3==1.9.70 \
    pycrypto==2.6.1 \
    afscripting==1.1.2 \
    afaws==0.1.7 \
    rfc3987==1.3.8 \
    ipython \
    pytest

# The following is supposed to decrease the size of the image,
# but doesn't seem to have any effect
RUN apk del --purge .build-deps

RUN mkdir /bluesky-aws/
WORKDIR /bluesky-aws/

ENV PATH="/bluesky-aws/bin/:${PATH}"
ENV PYTHONPATH="/bluesky-aws/:${PYTHONPATH}"

COPY bin/ /bluesky-aws/bin/
COPY blueskyaws/ /bluesky-aws/blueskyaws/

ARG UID=0
ARG GID=0

# TODO: if GID exists, leave that group as is, and use it
#   in the 'adduser' command
# TODO: if UID exists, leave that user as is and set that
#   user as the default

RUN if grep -q ":$GID:" /etc/group; \
    then \
        echo "Group $GID exists; renaming as blueskyaws"; \
        sed -i.bak -e "s/^.*:x:$GID/blueskyaws:x:$GID/g" /etc/group; \
    else \
        echo "Creating group $GID"; \
        addgroup -g $GID -S blueskyaws; fi

RUN if grep -q "x:$UID:" /etc/passwd; \
    then \
        echo "User $UID exists. Renaming as blueskyaws"; \
        sed -i.bak -e "s/^.*:x:$UID:.*$/blueskyaws:x:$UID:$GID:bluesky-aws user:\/home\/blueskyaws:\/bin\/bash/g" /etc/passwd; \
    else \
        echo "Creating User $UID"; \
        adduser -u $UID -G blueskyaws -S -s /bin/bash blueskyaws; fi

USER blueskyaws

CMD ec2-launch -h
