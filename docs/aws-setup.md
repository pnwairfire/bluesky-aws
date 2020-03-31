# AWS setup

The instructions in this doc assume thatyou already have an AWS account.

## Creating and Ec2 Instance & Installing Essentials

 - launch an ubuntu instance in the [EC2 admin console](https://us-west-2.console.aws.amazon.com/ec2/home)
   - make sure to specify a key pair that you have access to
   - create a security group that allows ssh access - [EC2 security group console](https://us-west-2.console.aws.amazon.com/ec2/home#SecurityGroups)
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
docker pull pnwairfire/bluesky:v4.1.34
docker run --rm pnwairfire/bluesky:v4.1.34 # this will print helpstring
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



## Launch and Setup an Instance for Running Admin App and run-bluesky

Note that these instructions use apache2 virtual hosts to proxy requests to
the bluesky-aws-admin web app.

 - Launch an ubuntu instance with essentials (see above) and ssh to it -- make sure to add a security group that opens ports 80 and 443 (in addition to 22 for ssh)
 - Using your domain regestrar, create an A Record or CNAME (whichever is appropriate) to point a sub-domain (we'll use 'foo' for these instructions) to the new instance
 - install apache and enable modules
```
sudo apt-get update
sudo apt-get install -y apache2
sudo a2enmod proxy_pass proxy_http ssl
sudo systemctl restart apache2
```
 - install docker-compose
```
sudo apt-get install -y docker-compose
```
 - optionally install tmux and a text editor
```
sudo apt-get install -y tmux emacs
```
 - install AWS credentials, which entails creating two files:
  - ~/.aws/config
```
[default]
region=us-west-2
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
git clone git@github.com:pnwairfire/bluesky-aws.git pnwairfire-bluesky-aws
cd pnwairfire-bluesky-aws
```
 - copy nextjs and nginx config files
```
cp bluesky-aws-admin/next.config.js.example bluesky-aws-admin/next.config.js
cp bluesky-aws-admin/nginx.conf.example bluesky-aws-admin/nginx.conf
```
 - Modify next.config.js and nginx.conf appropriately
 - build and run admin app
```
./reboot-admin  --yaml-file bluesky-aws-admin/docker-compose-prod.yml --rebuild --background
```

#### Configure apache
 - optionally install ssl certificates and configure apache to use it
 - optionally create .htpasswd file if you're going to use basic auth to password protect the admin site
```
sudo htpasswd -c /etc/apache2/.htpasswd bluesky-aws-user1  # replace 'bluesky-aws-user1' with desired username
sudo htpasswd /etc/apache2/.htpasswd bluesky-aws-user2
```
 - To configure an apache virtual host to proxy to the admin UI, create virtualhost config file `/etc/apache2/sites-available/foo.conf` containing something like following (modified appropriately). Basic auth and ssl configuration are optional.
```
SSLStrictSNIVHostCheck off

#NameVirtualHost *:443
<VirtualHost *:443>
        ServerAdmin webmaster@localhost
        ServerName foo.yourdomain.com
       ServerAlias www.foo.yourdomain.com

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

       ProxyPass / http://127.0.0.1:3030/
       ProxyPassReverse / http://127.0.0.1:3030/

       SSLProxyEngine on
       SSLEngine on
       SSLCertificateFile /etc/apache2/ssl/yourdomain.com/abc123.crt
       SSLCertificateKeyFile /etc/apache2/ssl/yourdomain.com/yourdomain.key
       SSLCertificateChainFile /etc/apache2/ssl/yourdomain.com/gd_bundle-g2-g1.crt
</VirtualHost>

<VirtualHost *:80>
  ServerName foo.yourdomain.com
  Redirect permanent / https://foo.yourdomain.com
</VirtualHost>
```
 - Verify that the config is valid, and then enable it and reload apache
```
sudo apachectl configtest
sudo a2ensite bluesky-aws.conf
sudo systemctl reload apache2
```

#### Running run-bluesky

 - created a new keypair in the [aws EC2 console](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#KeyPairs:) to use for running run-bluesky,  and install it on the new instance
 - install make
```
sudo apt-get install -y make
```
 - build bluesky-aws docker image for running run-bluesky
```
cd ~/code/pnwairfire-bluesky-aws
make build
```
 - run `run-bluesky`

##### cron
 - optionally schedule `run-bluesky` in cron (e.g. if you have fire data generated on a daily basis)
 - install mutt to receive mail on failures
```
sudo apt-get install mutt
mutt  # run it once to set up mail file
```
