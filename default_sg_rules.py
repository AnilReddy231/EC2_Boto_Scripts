import boto3
import json

ec2_client = boto3.client('ec2', verify=False)
response = ec2_client.describe_regions()
vpc_ids=[]
default_sg_ids=[]
mapping = {}
mapping['regions']=[]

regions=[region['RegionName'] for region in response['Regions']]
for region in regions:
        sg_ids=[]
        client = boto3.client('ec2', region_name=region, verify=False)
        vpcs_response=client.describe_vpcs()
        vpcs=[]
        for vpc in vpcs_response['Vpcs']:
                vpc_id=vpc['VpcId']
                sg_response=client.describe_security_groups(Filters=[{"Name":"vpc-id", "Values": [vpc_id]},{"Name":"group-name", "Values": ["default"]}])
                def_sec_grps={}
                for sg in sg_response['SecurityGroups']:
                        def_sec_grps["sg_id"]=sg['GroupId']
                        def_sec_grps["ingress"]=sg['IpPermissions']
                        def_sec_grps["egress"]=sg['IpPermissionsEgress']
                vpcs.append({"vpc_id": vpc_id, "default_sg": def_sec_grps})
        mapping['regions'].append({"region_name": region,
                                "vpcs":vpcs})

print(json.dumps(mapping,indent=4))

