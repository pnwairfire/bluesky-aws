FROM node:13.7.0-alpine3.11

RUN mkdir /bluesky-aws-admin/
WORKDIR /bluesky-aws-admin/
COPY package.json /bluesky-aws-admin/
RUN npm install

# We need to copy individual dirs and files, rather than copy entire dir,
# because copying bluesky-aws-admin/ includes node_modules and other
# .gitignore'd files and dirs
#COPY ./ /bluesky-aws-admin/

COPY bin/ /bluesky-aws-admin/bin/
COPY components/ /bluesky-aws-admin/components/
COPY lib/ /bluesky-aws-admin/lib/
COPY pages/ /bluesky-aws-admin/pages/
COPY public/ /bluesky-aws-admin/public/
COPY next.config.js /bluesky-aws-admin/next.config.js

RUN npm run build

CMD npm run start
