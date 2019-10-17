FROM python:3.7.1-alpine3.8

RUN apk add --update bash less vim curl

# The following build tools are for paramiko
RUN apk --update add --no-cache --virtual .build-deps \
        make automake gcc g++ \
    && apk --update add --no-cache \
        musl-dev libffi-dev openssl-dev python3-dev

RUN pip install --extra-index https://pypi.airfire.org/simple \
    paramiko==2.4.2 \
    boto3==1.9.70 \
    pycrypto==2.6.1 \
    afscripting==1.1.5 \
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

CMD ec2-launch -h
