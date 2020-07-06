# AWS setup

The instructions in this doc assume that you already have an AWS account.

## Creating and Ec2 Instance & Installing Essentials

 - launch an ubuntu instance in the [EC2 admin console](https://us-west-2.console.aws.amazon.com/ec2/home)
   - make sure to specify a key pair that you have access to
   - create a security group that allows ssh access and NFS access (port 2049) - [EC2 security group console](https://us-west-2.console.aws.amazon.com/ec2/home#SecurityGroups)
 - ssh to the EC2 instance
```
ssh -A ubuntu@IP_ADDRESS -i ~.ssh/ID_FILE
```
 - install docker
```
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install -y docker-ce
sudo systemctl status docker
```
 - add to docker group, logout, and log back in
```
sudo usermod -aG docker ${USER}
exit
ssh -A ubuntu@IP_ADDRESS -i ~.ssh/ID_FILE
```
 - Install NFS client
```
sudo apt-get install -y nfs-common
```
 - Install aws client
 ```
 sudo apt install -y awscli
 ```



## Create an EC2 AMI for Running Bluesky

 - Launch an ubuntu instance with essentials (see above), and ssh to it
 - pull bluesky image and verify that it works
```
docker pull pnwairfire/bluesky:v4.2.9
docker run --rm pnwairfire/bluesky:v4.2.9 # this will print helpstring
```
 - Install `at` for scheduling instance auto-termination
 ```
 sudo apt install -y at
 ```
 - create an image from the instance, and terminate it



## Create an S3 bucket

 - create a bucket in the [S3 AWS console](https://s3.console.aws.amazon.com/s3/home)



## Create an EFS Volume to store Met data

This is only necessary if running bluesky modules, such as hysplit
dispersion, that require met data.

 - Create an EFS volume in the [EFS admin console](https://us-west-2.console.aws.amazon.com/efs/home)
 - Once created, select the volume in the list of file systems, click 'Manage file system access', and then:
    - create mount target, if necessary
    - assign to the mount target whatever security group(s) you'll be using for your ec2 instance



## Launch and Setup an Instance for Running the Admin App, Receiving Met Data, and Running run-bluesky

Note that these instructions use apache2 to proxy requests to
the bluesky-aws-admin web app.

 - Launch an ubuntu instance with essentials (see above) and ssh to it -- make sure to add a security group that opens ports 80 and 443 (in addition to 22 for ssh and 2049 for NFS)
 - If using MET data in your bluesky runs, you'll need to mount the EFS volume that will hold the met data.  The [EFS admin console](https://us-west-2.console.aws.amazon.com/efs/home) provides instructions which include a command that looks something like the following.  Replace `HOSTNAME` and `/path/to/Met/` appropriately.
```
sudo mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport HOSTNAME:/ /path/to/Met/
```
 - If configuring apache with a VirtualHost for a particular subdomain (see below), then log into your domain regestrar and create an A Record or CNAME (whichever is appropriate) to point a sub-domain (we'll use 'foo' in the apache configuration instructions, below) to the new instance
 - install apache and enable modules
```
sudo apt-get update
sudo apt-get install -y apache2
sudo a2enmod proxy_http ssl
sudo systemctl restart apache2
```
 - install docker-compose
```
sudo apt-get install -y docker-compose
```
 - optionally install `tmux` (a terminal multiplexer) and a text editor (e.g. `vim` or `emacs`)
```
sudo apt-get install -y tmux emacs
```
 - install AWS credentials, which entails creating two files.  You can create these files manually or use `aws configure`.
  - ~/.aws/config
```
[default]
region=us-west-2
output=text
```
  - ~/.aws/credentials
```
[default]
aws_access_key_id = abc123
aws_secret_access_key = 123abc
```


#### Run admin app

 - clone repo
```
mkdir ~/code
cd ~/code
# You can clone via https if you haven't added your public key to your
# github account:
#  > git clone https://github.com/pnwairfire/bluesky-aws.git \
#     pnwairfire-bluesky-aws
git clone git@github.com:pnwairfire/bluesky-aws.git pnwairfire-bluesky-aws
cd pnwairfire-bluesky-aws
```
 - copy nextjs and nginx config files
```
cp bluesky-aws-admin/next.config.js.example bluesky-aws-admin/next.config.js
cp bluesky-aws-admin/nginx.conf.example bluesky-aws-admin/nginx.conf
```
 - Modify next.config.js and nginx.conf appropriately. (See the notes written in the `*.example` files.)
 - build and run admin app
```
./reboot-admin  --yaml-file bluesky-aws-admin/docker-compose-prod.yml --rebuild --background
```

#### Apache

##### Config files

To configure apache to proxy requests to the admin site, and to
optionally support basic auth and ssl, you'll do one of the following

 1. modify one or both of the default config files:
```
/etc/apache2/sites-available/000-default.conf
/etc/apache2/sites-available/default-ssl.conf
```
 2. create a new virtualhost config file, `/etc/apache2/sites-available/foo.conf`, containing something like following basic structire

```
SSLStrictSNIVHostCheck off

#NameVirtualHost *:443
<VirtualHost *:443>
        ServerAdmin webmaster@localhost
        ServerName foo.yourdomain.com
       ServerAlias www.foo.yourdomain.com


       # Proxy, ssl, and basic auth configuration
       # go here. See sections below for details.


</VirtualHost>

<VirtualHost *:80>
  ServerName foo.yourdomain.com
  Redirect permanent / https://foo.yourdomain.com
</VirtualHost>
```

The followig `Configure *` sections describe the details of what needs to be
added to the config file(s).


###### Configure Proxying

```
       ProxyPass / http://127.0.0.1:3030/
       ProxyPassReverse / http://127.0.0.1:3030/

       SSLProxyEngine on
```

###### Configure SSL (optioanl)

To enable ssl, first install install your ssl certificates and
then add the following to your apache config:

```
       SSLEngine on
       SSLCertificateFile /etc/apache2/ssl/yourdomain.com/abc123.crt
       SSLCertificateKeyFile /etc/apache2/ssl/yourdomain.com/yourdomain.key
       SSLCertificateChainFile /etc/apache2/ssl/yourdomain.com/gd_bundle-g2-g1.crt
```

###### Configure Basic Auth (optional)

To use basic auth to password protect the admin site, first create an .htpasswd file:

```
sudo htpasswd -c /etc/apache2/.htpasswd bluesky-aws-user1  # replace 'bluesky-aws-user1' with desired username
sudo htpasswd /etc/apache2/.htpasswd bluesky-aws-user2
```

And then ADd the following to your apache config:

```
       <Location />
                 AuthType Basic
                 AuthName "Authentication Required"
                 AuthUserFile "/etc/apache2/.htpasswd"
                 Require valid-user
       </Location>
       <Location /output/ >
                 Allow From All
                 Satisfy Any
       </Location>
```

##### Reloading

If using a new apache virtualhost, first run the following to enable the site:
```
sudo a2ensite bluesky-aws.conf
```

Finally, verify that the config updates are valid, and reload apache.
```
sudo apachectl configtest
sudo systemctl reload apache2
```


#### Running run-bluesky

 - created a new keypair in the [aws EC2 console](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#KeyPairs:) that will be used by the `run-bluesky` process to ssh to the instances that it launches,  and install it on the instance you created to run `run-bluesky`
 - install make
```
sudo apt-get install -y make
```
 - build bluesky-aws docker image for running run-bluesky
```
cd ~/code/pnwairfire-bluesky-aws
make build
```
 - run `run-bluesky` (See the [configuration doc](./configuration.md) for information on setting up and configuring your run.)
```
docker run --rm -ti --user blueskyaws bluesky-aws ./bin/run-bluesky -h
```

##### cron
 - optionally schedule `run-bluesky` in cron (e.g. if you have fire data generated on a daily basis)
 - optionall schedule `make update_to_latest_tag_and_bounce` to automatically run the latest tagged version of `bluesky-aws` as it becomes available.
 - install mutt to receive mail on failures
```
sudo apt-get install mutt
mutt  # run it once to set up mail file
```
