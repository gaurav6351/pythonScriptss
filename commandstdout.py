#!/usr/bin/env python
import argparse
import commands
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Check DNS for Mesos Hosts")
    parser.add_argument('--env', action="store", required=True)
    return parser.parse_args()


def lookup_sg(env):
    if env == "staging":
        return ("us-east-1","sg")
    elif env == "production":
        return ("us-west-1","sg")

    # Replace with boto3 equivalent
def get_instances(env):
    print(env)
    cmd="aws ec2 describe-instances --region {} --query 'Reservations[*].Instances[*].[PublicDnsName,Tags[?Key==`Name`].Value]' --filters \"Name=instance-state-name,Values=running\" \"Name=instance.group-id,Values={}\"".format(*lookup_sg(env))
    return commands.getstatusoutput(cmd)


def get_public_dns_name_this_host():
    os.system('curl -s http://169.254.169.254/latest/meta-data/public-hostname > pub_dns_name')
    with open('pub_dns_name', 'r') as fd:
        return fd.readline().strip()


def dns_entry_exists(hostname):
    status, out = commands.getstatusoutput("dig +short {} | wc -l".format(hostname))
    if status != 0:
        print(status,out)
        return False
    else:
        try:
            n = int(out)
            return n != 0
        except:
            return False


def dns_entry_create():
    dns_name = get_public_dns_name_this_host()

    route53_rec["Changes"][0]['ResourceRecordSet']["ResourceRecords"][0]['Value'] = dns_name
    route53_rec["Changes"][0]['ResourceRecordSet']["Name"] = "{0}.".format(hostname)

    with open('route_53_entry.json', 'w') as fd:
        fd.write(json.dumps(route53_rec))
        print(json.dumps(route53_rec))

    os.system(
        "aws route53 change-resource-record-sets --hosted-zone-id  --change-batch file://route_53_entry.json"
    )


def parse_output(cmd_out):
    js = json.loads(cmd_out)
    return [{"public_dns": j[0][0], "fqdn": j[0][1][0]} for j in js]

if __name__ == '__main__':
    args = parse_args()
    print args
    status, output = get_instances(args.env)
    if status != 0:
        print("cannot get output for " + args.env)
        sys.exit(1)
    servers = parse_output(output)
    for server in servers:
        if not dns_entry_exists(server["fqdn"]):
         dns_entry_create()
        else:
            print("OK "+ server["fqdn"])
