import boto3

def get_all_Instances():

    client = boto3.client('ec2')
    regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['running','stopped']
        }
        ]
    profiles = ['default','Jenkins']
    for profile in profiles:
        session = boto3.Session(profile_name=profile)
        print(f"Listing instances under Profile:{profile}")
        for region in regions:
            ec2_conn=session.resource('ec2',region_name=region)
            instances=ec2_conn.instances.filter(Filters=filters)
            for instance in instances:
                print(instances)
                print(instance.id, instance.instance_type, region)

if __name__ == '__main__':
    get_all_Instances()
