#!/usr/bin/env python
#take a snapshot and delete the detached volumes
import boto3

def get_detached_volumes(resource):
    volumes = resource.volumes.filter()
    return [ volume.id for volume in volumes if volume.state == 'available' ]

def create_snapshot(ec2_conn, vol_id):
    snap = ec2_conn.create_snapshot(VolumeId=vol_id,
            Description=f"Last backup of volume {vol_id}")
    print(snap)

def main():
    ec2_conn = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_conn.describe_regions()['Regions']]
    for region in regions:
    	resource= boto3.resource('ec2',region_name=region)
        all_detached = get_detached_volumes(resource)
    for vol in all_detached:
        print(f"Creating snapshot for vol: {vol}")
        create_snapshot(ec2_conn, vol)
		print(f"Deleting volume {vol}")
        ec2_conn.delete_volume(VolumeId=vol)

if __name__ == "__main__":
    main()