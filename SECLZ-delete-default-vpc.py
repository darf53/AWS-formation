import json
import boto3

VERBOSE=0

def lambda_handler(event, context):

    regionList = []
    region = boto3.client('ec2')
    regions = region.describe_regions()

    for r in range(0, len(regions['Regions'])):

        regionaws = regions['Regions'][r]['RegionName']

        client = boto3.client('ec2', region_name = regionaws)
        response = client.describe_vpcs()

        for vpc in response['Vpcs']:

            if vpc['IsDefault'] == True:

                # set VPC id
                vpc_id = vpc['VpcId']
                print("Found default VPC in region",regionaws,": ",vpc_id)
                resource = boto3.resource('ec2', region_name = regionaws)
                vpcResources = resource.Vpc(vpc_id)
                # print(vpcResources)

                # Delete the IGW
                igws = vpcResources.internet_gateways.all()
                for igw in igws:
                    try:
                        print("Detaching and Removing igw-id: ", igw.id) if (VERBOSE == 1) else ""
                        igw.detach_from_vpc(VpcId=vpc_id)
                        igw.delete()
                    except boto3.exceptions.Boto3Error as e:
                        print(e)
                    print("Deleted internet GW:", igw)

                # Delete subnets
                subnets = vpcResources.subnets.all()
                for subnet in subnets:
                    try:
                        print("Deleting subnet: ", subnet.id) if (VERBOSE == 1) else ""
                        subnet.delete()
                    except boto3.exceptions.Boto3Error as e:
                        print(e)
                    print("Deleted subnet:", subnet)

                # Delete default VPC
                try:
                    print("Deleting default VPC: ", vpc_id) if (VERBOSE == 1) else ""
                    vpcResources.delete()
                except boto3.exceptions.Boto3Error as e:
                    print(e)
                print("Deleted default VPC:", vpc_id)
