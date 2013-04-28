import boto
import boto.ec2
import argparse
from boto.route53.record import ResourceRecordSets
import time
import sys
import logging


AWSAccessKeyId="Enter you AWS credentials here"
AWSSecretKey="Enter your AWS key here"


instance_types = [ 't1.micro', 'm1.small', 'm1.medium', 'm1.large', 'm1.xlarge', 'm3.xlarge', 
                    'm3.2xlarge','m2.xlarge', 'm2.2xlarge', 'm2.4xlarge', 'c1.medium', 'c1.xlarge', 
                    'cc2.8xlarge', 'cr1.8xlarge', 'cg1.4xlarge', 'hi1.4xlarge', 'hs1.8xlarge' ]

def add_dns_cname(ROUTE53_ZONE_NAME, record, cname):
    conn = boto.route53.connection.Route53Connection(AWSAccessKeyId,AWSSecretKey)
    results = conn.get_all_hosted_zones()
    zones = results['ListHostedZonesResponse']['HostedZones']
    found = 0
    for zone in zones:
        if zone['Name'] == ROUTE53_ZONE_NAME:
            found = 1
            break
    if not found:
        return "::ERROR:: No Route53 zone found for %s" % ROUTE53_ZONE_NAME
        
    zone_id = zone['Id'].replace('/hostedzone/', '')
    changes = ResourceRecordSets(conn, zone_id)
    change  = changes.add_change("CREATE", record + ROUTE53_ZONE_NAME, "CNAME", 60)
    change.add_value(cname)
    changes.commit()
    
    return "\nDNS: " + record + ROUTE53_ZONE_NAME + " -> " + cname
    
    
def launch_new_instance(ami, name, size, security_group, domain, launch_key):
    conn = boto.ec2.EC2Connection(AWSAccessKeyId,AWSSecretKey)
    user_data = "#!/bin/bash"
    user_data += "\nhostname " + name + domain
    # you can do other stuff here like installing packages to be installed upon launch
    user_data += "\necho \"" + name + domain + "\" > /etc/hostname"
    user_data += "\ntouch /var/log/cloud_init.done"

    print "\n\nHold onto your seats, your instance is being launched ..."
    launched_instances = conn.run_instances(
                            ami, 
                            min_count=1, 
                            max_count=1, 
                            key_name=launch_key, 
                            security_groups=[security_group], 
                            user_data=user_data, 
                            addressing_type=None, 
                            instance_type=size, 
                            placement=None, 
                            kernel_id=None, 
                            ramdisk_id=None, 
                            monitoring_enabled=False, 
                            subnet_id=None, 
                            block_device_map=None, 
                            disable_api_termination=False, 
                            instance_initiated_shutdown_behavior=None, 
                            private_ip_address=None, 
                            placement_group=None, 
                            client_token=None, 
                            security_group_ids=None, 
                            additional_info=None, 
                            instance_profile_name=None, 
                            instance_profile_arn=None, 
                            tenancy=None, 
                            ebs_optimized=False)
    
    time.sleep(10)
    
    while launched_instances.instances[0].update() != "running":
        print "\nWaiting for instance to be launched. Sleeping for 10 secs..."
        time.sleep(10)
        
    print "\nLets sleep for another 10 seconds..."
    time.sleep(10)
    
    launched_instances.instances[0].add_tag("Name", value = name)
    ret = "Launched instance in EC2\n"
    ret += "AMI: " + ami + "\n"
    ret += "Name: " + name + "\n"
    ret += "Size: " + size + "\n"
    ret += "Security Group: " + security_group + "\n"
    if domain == "localhost":
        print "Skipping DNS add as no `--domain` specified."
    else:
        ret += add_dns_cname(domain , name, launched_instances.instances[0].public_dns_name)
    
    print ret
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Launch some ec2 boxes.')
    parser.add_argument('--name', type=str)
    parser.add_argument('--size', type=str)
    parser.add_argument('--security_group', type=str)
    parser.add_argument('--domain', type=str)
    parser.add_argument('--launch_key', type=str)
    parser.add_argument('--ami', type=str)
    args = parser.parse_args()
    
    if AWSAccessKeyId == "Enter you AWS credentials here" or AWSSecretKey == "Enter your AWS key here":
        print "Hold your horses there bud. You need to edit this file and fill in your credentials.\nAKA, set the values of these two varables - AWSAccessKeyId, AWSSecretKey"
        exit(0)
    
    #lets attempt to get details interactively
    if args.name == None:
        args.name = raw_input("Enter the a name for your instance: ")
    if args.size == None:
        args.size = raw_input("Enter a valid ec2 size for the instance (eg. m1.small): ")
    if args.security_group == None:
        args.security_group = raw_input("Enter a valid security group to place the instance into: ")
    if args.domain == None:
        args.domain = raw_input("Enter a domain to add a DNS entry to (must be a valid route53 domain / enter blank for none): ")
    if args.launch_key == None:
        args.launch_key = raw_input("Enter a valid launch key for the instance: ")
    if args.ami == None:
        args.ami = raw_input("Enter an AMI to use to launch this instance [default: ami-3fec7956 (ubuntu 12.04)]: ")
    
    if args.ami == "":
        args.ami = "ami-3fec7956"
    
    if args.size not in instance_types:
        logging.error("I did not get a valid size from you for the instance, valid sizes are: \n")
        print ", ".join(instance_types)
    
    if args.domain == "" or args.domain == None:
        args.domain = "localhost"
        

    launch_new_instance(args.ami, args.name, args.size, args.security_group, args.domain, args.launch_key)