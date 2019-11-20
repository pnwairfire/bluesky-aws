# AWS setup

 - create an AWS account
 - launch an ubuntu instance in the [EC2 admin console](https://us-west-2.console.aws.amazon.com/ec2/home), making sure to specify a key pair that you have access to
 - ssh to the EC2 instance and install docker
```
ssh ubuntu@IP_ADDRESS -i ~.ssh/ID_FILE
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
ssh ubuntu@IP_ADDRESS -i ~.ssh/ID_FILE
```
 - pull bluesky image, verify that it works, and logout
```
docker pull pnwairfire/bluesky:v4.1.27
docker run --rm pnwairfire/bluesky:v4.1.27
exit
```
 - Install aws client
 ```
 sudo apt install -y awscli
 ```
 - create an image from the image, and terminate it
 - create a bucket in the [S3 AWS console](https://s3.console.aws.amazon.com/s3/home)
 - create a security group that allows ssh access - [EC2 security group console](https://us-west-2.console.aws.amazon.com/ec2/home#SecurityGroups)
