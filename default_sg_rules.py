import boto3
import json
import sys, time
import argparse
import logging

def default_security_groups():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_regions()
    mapping = {}
    mapping['regions'] = []

    regions = [region['RegionName'] for region in response['Regions']]
    for region in regions:
        sg_ids=[]
        client = boto3.client('ec2', region_name=region)
        vpcs_response = client.describe_vpcs()
        vpcs=[]
        for vpc in vpcs_response['Vpcs']:
            vpc_id = vpc['VpcId']
            sg_response = client.describe_security_groups(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}, {"Name": "group-name", "Values": ["default"]}])
            def_sec_grps = {}
            for sg in sg_response['SecurityGroups']:
                def_sec_grps["sg_id"]=sg['GroupId']
                def_sec_grps["ingress"]=sg['IpPermissions']
                def_sec_grps["egress"]=sg['IpPermissionsEgress']
            vpcs.append({"vpc_id": vpc_id, "default_sg": def_sec_grps})
        if vpcs:
            mapping['regions'].append({"region_name": region,"vpcs":vpcs})
    return mapping


def print_json(json_object):
    logging.info(f"Dumping the Default SG details in JSON format")
    print(json.dumps(json_object, indent=4))


def delete_sg_rules(json_object):
    logging.info(f"Proceeding on to deleting the rules from default SGs")
    for region in json_object['regions']:
        ec2_resource = boto3.resource ('ec2', region_name=region['region_name'])
        for vpc in region['vpcs']:
            sg=vpc['default_sg']
            logging.info(f"Deleting rules from security_group:{sg['sg_id']} in Region:{region['region_name']}")
            security_group = ec2_resource.SecurityGroup(sg['sg_id'])
            if sg['ingress']:   # If rules are not empty
                logging.info (f"Deleting the Ingress rules from default SG: {sg['sg_id']}")
                security_group.revoke_ingress(IpPermissions=sg['ingress'])
            if sg['egress']:
                logging.info (f"Deleting the Egress rules from default SG: {sg['sg_id']}")
                security_group.revoke_egress(IpPermissions=sg['egress'])


def add_rule_sg(region ,sg_id,ingress,egress):
    logging.info(f"Adding the Rules to SGs")
    client = boto3.client ('ec2', region_name=region)
    client.authorize_security_group_ingress(GroupId=sg_id, IpPermissions=json.loads(ingress))
    client.authorize_security_group_egress(GroupId=sg_id, IpPermissions=json.loads(egress))


def arg_parse(*args, **kwargs):
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Program to display all the default security groups along with their rules. And Deletes them if requested to.",
        prog=sys.argv[0],
    )

    parser.add_argument(
        "-v", "--verbose",
        action='count',
        help="Display verbose output; can be used more than once for greater verbosity."
    )
    switch_group = parser.add_mutually_exclusive_group (required=True)

    switch_group.add_argument(
        "-S", "--describe",
        action='store_true',
        help="Describes Default SG Details",
    )

    switch_group.add_argument (
        "-D", "--delete",
        action='store_true',
        help="Deletes Default SG Rules",
    )

    switch_group.add_argument (
        "-A", "--add",
        action='store_true',
        help="Adds Rule to SGs",
    )

    parser.add_argument (
        "-rg", "--region",
        action='store',
        help="Region Name",
        dest='rg_id'
    )

    parser.add_argument(
        "-sg", "--security-group",
        action='store',
        help="SG Id",
        dest='sg_id'
    )

    parser.add_argument(
        "-in", "--ingress-rule",
        action='store',
        help="Ingress Rule",
        dest='inbound'
    )

    parser.add_argument(
        "-out", "--egress-rule",
        action='store',
        help="Egress Rule",
        dest='outbound'
    )

    parsed = parser.parse_args()

    log = Logging(0)
    if parsed.verbose is not None:
        if parsed.verbose == 1:
            log = Logging(1)
        elif parsed.verbose > 1:
            log = Logging(2)

    all_default_sg = default_security_groups ()

    if parsed.describe is True:
        print_json(all_default_sg)
    if parsed.delete is True:
        print_json(all_default_sg)
        delete_sg_rules(all_default_sg)
    # print(type(json.loads(parsed.inbound)[0]))
    if parsed.add is True:
        add_rule_sg(parsed.rg_id, parsed.sg_id,parsed.inbound,parsed.outbound)

    logging.info(f'Processed in {round(time.time() - start_time)} seconds.')


if __name__ == '__main__':
        logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
        sys.exit(arg_parse(*sys.argv))