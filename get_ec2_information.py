# author : lavaraja padala
# email : lavaraja.padala@gmail.com


import boto3

import sys

import datetime
import pandas as pd

#Need to configure aws access key and secrey in awscli.
# For more info https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html

ec2=boto3.client('ec2')
response2=ec2.describe_instances()

# We can pass the instanceIDs to get details for only few instances. The response is a dictionary. for more information https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

#
# response = client.describe_instances(
#     Filters=[
#         {
#             'Name': 'string',
#             'Values': [
#                 'string',
#             ]
#         },
#     ],
#     InstanceIds=[
#         'string',
#     ],
#     DryRun=True|False,
#     MaxResults=123,
#     NextToken='string'
# )

# [{'AmiLaunchIndex': 0, 'ImageId': 'ami-0cc96feef8c6bbff3', 'InstanceId': 'i-09cf49a7304758bd3', 'InstanceType': 't2.micro', 'KeyName': 'iopstest', 'LaunchTime': datetime.datetime(2019, 6, 21, 16, 29, 52, tzinfo=tzutc()), 'Monitoring': {'State': 'disabled'}, 'Placement': {'AvailabilityZone': 'us-east-1b', 'GroupName': '', 'Tenancy': 'default'}, 'PrivateDnsName': 'ip-172-31-40-64.ec2.internal', 'PrivateIpAddress': '172.31.40.64', 'ProductCodes': [], 'PublicDnsName': 'ec2-54-90-224-154.compute-1.amazonaws.com', 'PublicIpAddress': '54.90.224.154', 'State': {'Code': 16, 'Name': 'running'}, 'StateTransitionReason': '', 'SubnetId': 'subnet-0c67ec51', 'VpcId': 'vpc-ffa38987', 'Architecture': 'x86_64', 'BlockDeviceMappings': [{'DeviceName': '/dev/xvda', 'Ebs': {'AttachTime': datetime.datetime(2019, 6, 21, 16, 29, 53, tzinfo=tzutc()), 'DeleteOnTermination': True, 'Status': 'attached', 'VolumeId': 'vol-01056d0b796108524'}}], 'ClientToken': '', 'EbsOptimized': False, 'EnaSupport': True, 'Hypervisor': 'xen', 'NetworkInterfaces': [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-54-90-224-154.compute-1.amazonaws.com', 'PublicIp': '54.90.224.154'}, 'Attachment': {'AttachTime': datetime.datetime(2019, 6, 21, 16, 29, 52, tzinfo=tzutc()), 'AttachmentId': 'eni-attach-055d9e8591296f5bd', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'}, 'Description': '', 'Groups': [{'GroupName': 'launch-wizard-1', 'GroupId': 'sg-09cd274af9ee697fe'}], 'Ipv6Addresses': [], 'MacAddress': '0e:af:51:cb:5e:64', 'NetworkInterfaceId': 'eni-0342286942dbbd8e1', 'OwnerId': '381815327666', 'PrivateDnsName': 'ip-172-31-40-64.ec2.internal', 'PrivateIpAddress': '172.31.40.64', 'PrivateIpAddresses': [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-54-90-224-154.compute-1.amazonaws.com', 'PublicIp': '54.90.224.154'}, 'Primary': True, 'PrivateDnsName': 'ip-172-31-40-64.ec2.internal', 'PrivateIpAddress': '172.31.40.64'}], 'SourceDestCheck': True, 'Status': 'in-use', 'SubnetId': 'subnet-0c67ec51', 'VpcId': 'vpc-ffa38987', 'InterfaceType': 'interface'}], 'RootDeviceName': '/dev/xvda', 'RootDeviceType': 'ebs', 'SecurityGroups': [{'GroupName': 'launch-wizard-1', 'GroupId': 'sg-09cd274af9ee697fe'}], 'SourceDestCheck': True, 'VirtualizationType': 'hvm', 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}, 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}, 'HibernationOptions': {'Configured': False}}]


instance_report=[]
for instances in response2.get("Reservations"):
    for instance in instances.get("Instances"):

        InstanceId=instance.get("InstanceId")
        InstanceType=instance.get("InstanceType")

        for volume in instance.get("BlockDeviceMappings"):
            data=[InstanceId,InstanceType,volume.get("DeviceName"),volume.get("Ebs").get("VolumeId"),0,0]
            instance_report.append(data)

# If we need more information we can add those fields to our dataframe.

print("Generated instance report with associated Volume ID's :")
print("\n")

instance_report = pd.DataFrame(instance_report,columns=['InstanceId', 'InstanceType', 'DeviceName', 'VolumeId','Size','Iops'])

print(instance_report.sort_values(by=['InstanceId', 'VolumeId'], ascending=False))
print("\n")


# To get IOPS and SIZE for the associated volumes. This will help in reviewing the IOPS asscoated to particular volume.


response = ec2.describe_volumes( VolumeIds=list(instance_report.VolumeId.unique()))
report = []

for volume in response.get("Volumes"):
    if not volume.get("Iops") is None:
        for attach in volume.get("Attachments"):
            InstanceID = attach.get("InstanceId")
        VolumeId = attach.get("VolumeId")
        # print(VolumeId)
        row = [VolumeId, volume.get("Size"), volume.get("Iops"), volume.get("VolumeType"), InstanceID]
        report.append(row)





ebs_volume_info = pd.DataFrame(report,columns=['VolumeId', 'Size', 'Iops', 'VolumeType', 'InstanceID'])

print("Volumes and their IOPS details:")
print("\n")
print(ebs_volume_info.sort_values(by=['Iops', 'Size'], ascending=False))
print("\n")


print("Volumes having more IOPS defined than default suggested by aws :")
# for more details https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
print("\n")
print(ebs_volume_info[(ebs_volume_info.Iops > 3*ebs_volume_info.Size )])
print("\n")
