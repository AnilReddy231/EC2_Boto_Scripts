import boto3
import sys
import argparse
import logging
from botocore.exceptions import ClientError
from time import sleep
import pdb

def arg_parse(*args, **kwargs):
    parser = argparse.ArgumentParser(
        description=f"Program to Delete All the Dependencies of the VPC followed by VPC too." \
                    f"\n Order of operations" \
                    f"\n 1.) Terminates the Instances" \
                    f"\n 2.) Deletes subnets" \
                    f"\n 3.) Detach and Delete the internet gateway" \
                    f"\n 4.) Deletes VPC Peering Connections" \
                    f"\n 5.) Deletes Non-Default Security Groups" \
                    f"\n 6.) Detach and Deletes Non-Main Route Tables" \
                    f"\n 7.) Deletes VPC EndPoints" \
                    f"\n 8.) Deletes the VPC "
        ,
        prog=sys.argv[0],
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument (
        "-vpc", "--vpc-id",
        action='store',
        help="VPC Id",
        dest='vpc'
    )

    parser.add_argument (
        "-rg", "--region",
        action='store',
        help="Region",
        dest='region'
    )

    parsed = parser.parse_args ()

    vpc_cleanup(parsed.vpc, parsed.region)


def vpc_cleanup(vpcid, region):
    """Remove VPC from AWS
    :param vpcid: id of vpc to delete
    :param region: region name where VPC is existing
    """
    logging.info(f'Removing VPC __{vpcid}__ from AWS')
    ec2_resource = boto3.resource('ec2', region_name=region)
    ec2_client = ec2_resource.meta.client
    vpc = ec2_resource.Vpc(vpcid)
    #pdb.set_trace()
    try:
        for subnet in vpc.subnets.all():
            for instance in subnet.instances.all():
                try:
                    logging.info(f"Terminating the instance __{instance.id}__ associated with the vpc __{vpc.id}__")
                    instance.terminate()
                    logging.info("Waiting for 60 seconds to let the instance be terminated")
                    sleep(60)
                except ClientError as e:
                    logging.error(e.response['Error']['Message'])

        for subnet in vpc.subnets.all():
            for interface in subnet.network_interfaces.all():
                try:
                    logging.info(f"Deleting the ENI __{interface.id}__ associated with the vpc __{vpc.id}__")
                    interface.delete()
                except ClientError as e:
                    logging.error(e.response['Error']['Message'])
            try:
                logging.info(f"Deleting the ENI __{subnet.id}__ associated with the vpc __{vpcid}__")
                subnet.delete()
            except ClientError as e:
                logging.error(e.response['Error']['Message'])

        for gw in vpc.internet_gateways.all():
            try:
                logging.info(f"detaching and deleting Internet Gateway __{gw.id}__ associated with the vpc __{vpc.id}__")
                vpc.detach_internet_gateway(InternetGatewayId=gw.id)
                gw.delete()
            except ClientError as e:
                logging.error(e.response['Error']['Message'])

        for requested_peer in vpc.requested_vpc_peering_connections.all():
            try:
                logging.info(f"Deleting VPC Peering Connection __{requested_peer.id}__ associated with the vpc __{vpc.id}__")
                requested_peer.delete()
            except ClientError as e:
                logging.error(e.response['Error']['Message'])

        for accepted_peer in vpc.accepted_vpc_peering_connections.all():
            try:
                logging.info(f"Deleting VPC Peering Connection __{accepted_peer.id}__ associated with the vpc __{vpc.id}__")
                accepted_peer.delete()
            except ClientError as e:
                logging.error(e.response['Error']['Message'])

        for sg in vpc.security_groups.all():
            if sg.group_name != 'default':
                try:
                    logging.info(f"Deleting the Security Group __{sg.id}__ associated with the vpc __{vpc.id}__")
                    sg.delete()
                except ClientError as e:
                    logging.error(e.response['Error']['Message'])

        route_tables = vpc.route_tables.all()
        for route_table in route_tables:
            for route in route_table.routes:
                if route.origin == 'CreateRoute':
                    try:
                        logging.info(f"Deleting the routes from __{route_table.id}__ of vpc __{vpc.id}__")
                        print(route)
                        route.delete()
                    except ClientError as e:
                        logging.error(e.response['Error']['Message'])
            for association in route_table.associations:
                if not association.main:
                    try:
                        logging.info(f"Disassociating and Deleting the non-main route table __{route_table.id}__ of the vpc __{vpc.id}__")
                        association.delete()
                    except ClientError as e:
                        logging.error(e.response['Error']['Message'])
        for route_table in route_tables:
            if not route_table.associations:  # If Empty
                try:
                    logging.info(f"Deleting the route table __{route_table.id}__ of vpc __{vpc.id}__")
                    route_table.delete()
                except ClientError as e:
                    logging.error(e.response['Error']['Message'])

        for endpoint in ec2_client.describe_vpc_endpoints(Filters=[{
                    'Name': 'vpc-id',
                    'Values': [vpcid]
                }])['VpcEndpoints']:
            try:
                logging.info(f"Deleting the VPC Endpoint __{endpoint['VpcEndpointId']}__ of the vpc __{vpc.id}__")
                ec2_client.delete_vpc_endpoints(VpcEndpointIds=[endpoint['VpcEndpointId']])
            except ClientError as e:
                logging.error(e.response['Error']['Message'])

        try:
            logging.info(f"All the Dependencies of the VPC __{vpc.id}__ are being removed. Proceeding on to Deleting the VPC")
            ec2_client.delete_vpc(VpcId=vpc.id)
        except ClientError as e:
            logging.error(e.response['Error']['Message'])
    except ClientError as e:
        logging.error(e.response['Error']['Message'])


if __name__ == '__main__':
    logging.basicConfig (format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
    sys.exit(arg_parse(*sys.argv))
