pyec2launcher
=============

taxi checklist
--------------
* python 2.7
* boto `pip install boto` (https://github.com/boto/boto)
* AWS account and Credentials

pre-flight
----------
you need to know the following
* AWS account credentials (http://aws.amazon.com/iam/)
* create the appropriate group in EC2
* create and download a keypair in ec2, remember the name (you will launch the instance with this key, and SSH to it initially using this)

runway preparation
------------------
* edit the `pyec2launcher.py` file and insert your AWS credentials
* determine the security group you would like to place the instance in
* determine the AMI you would like to use
* determine the launch keypair you would like to use, and create if necessary



