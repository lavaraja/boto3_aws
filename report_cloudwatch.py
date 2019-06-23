#Author : lavaraja
#email : lavaraja.padala@gmail.com

import boto3

import sys

import datetime
import pandas as pd
from cloudwatch_metric import collect_metrics_ebs_volume

#import colored
ec2=boto3.client('ec2')

##### **** change start date and end date as needed ***** ####

startdate=datetime.datetime(2019, 6, 21)
enddate=datetime.datetime(2019, 6, 27)


response2=ec2.describe_instances()
instance_report=[]

# [{'AmiLaunchIndex': 0, 'ImageId': 'ami-0cc96feef8c6bbff3', 'InstanceId': 'i-09cf49a7304758bd3', 'InstanceType': 't2.micro', 'KeyName': 'iopstest', 'LaunchTime': datetime.datetime(2019, 6, 21, 16, 29, 52, tzinfo=tzutc()), 'Monitoring': {'State': 'disabled'}, 'Placement': {'AvailabilityZone': 'us-east-1b', 'GroupName': '', 'Tenancy': 'default'}, 'PrivateDnsName': 'ip-172-31-40-64.ec2.internal', 'PrivateIpAddress': '172.31.40.64', 'ProductCodes': [], 'PublicDnsName': 'ec2-54-90-224-154.compute-1.amazonaws.com', 'PublicIpAddress': '54.90.224.154', 'State': {'Code': 16, 'Name': 'running'}, 'StateTransitionReason': '', 'SubnetId': 'subnet-0c67ec51', 'VpcId': 'vpc-ffa38987', 'Architecture': 'x86_64', 'BlockDeviceMappings': [{'DeviceName': '/dev/xvda', 'Ebs': {'AttachTime': datetime.datetime(2019, 6, 21, 16, 29, 53, tzinfo=tzutc()), 'DeleteOnTermination': True, 'Status': 'attached', 'VolumeId': 'vol-01056d0b796108524'}}], 'ClientToken': '', 'EbsOptimized': False, 'EnaSupport': True, 'Hypervisor': 'xen', 'NetworkInterfaces': [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-54-90-224-154.compute-1.amazonaws.com', 'PublicIp': '54.90.224.154'}, 'Attachment': {'AttachTime': datetime.datetime(2019, 6, 21, 16, 29, 52, tzinfo=tzutc()), 'AttachmentId': 'eni-attach-055d9e8591296f5bd', 'DeleteOnTermination': True, 'DeviceIndex': 0, 'Status': 'attached'}, 'Description': '', 'Groups': [{'GroupName': 'launch-wizard-1', 'GroupId': 'sg-09cd274af9ee697fe'}], 'Ipv6Addresses': [], 'MacAddress': '0e:af:51:cb:5e:64', 'NetworkInterfaceId': 'eni-0342286942dbbd8e1', 'OwnerId': '381815327666', 'PrivateDnsName': 'ip-172-31-40-64.ec2.internal', 'PrivateIpAddress': '172.31.40.64', 'PrivateIpAddresses': [{'Association': {'IpOwnerId': 'amazon', 'PublicDnsName': 'ec2-54-90-224-154.compute-1.amazonaws.com', 'PublicIp': '54.90.224.154'}, 'Primary': True, 'PrivateDnsName': 'ip-172-31-40-64.ec2.internal', 'PrivateIpAddress': '172.31.40.64'}], 'SourceDestCheck': True, 'Status': 'in-use', 'SubnetId': 'subnet-0c67ec51', 'VpcId': 'vpc-ffa38987', 'InterfaceType': 'interface'}], 'RootDeviceName': '/dev/xvda', 'RootDeviceType': 'ebs', 'SecurityGroups': [{'GroupName': 'launch-wizard-1', 'GroupId': 'sg-09cd274af9ee697fe'}], 'SourceDestCheck': True, 'VirtualizationType': 'hvm', 'CpuOptions': {'CoreCount': 1, 'ThreadsPerCore': 1}, 'CapacityReservationSpecification': {'CapacityReservationPreference': 'open'}, 'HibernationOptions': {'Configured': False}}]
for instances in response2.get("Reservations"):
    for instance in instances.get("Instances"):

        InstanceId=instance.get("InstanceId")
        InstanceType=instance.get("InstanceType")

        for volume in instance.get("BlockDeviceMappings"):
            data=[InstanceId,InstanceType,volume.get("DeviceName"),volume.get("Ebs").get("VolumeId"),0,0,'abc@abc.com',False,0]
            instance_report.append(data)



print("Generated instance report with associated Volume ID's :")
print("\n")

instance_report = pd.DataFrame(instance_report,columns=['InstanceId', 'InstanceType', 'DeviceName', 'VolumeId','Size','Iops','Owner','Optimization_required','Suggested_IOps_Setting'])

print(instance_report.sort_values(by=['InstanceId', 'VolumeId'], ascending=False))
print("\n")
# to get unique list of ebs volume Id's
#print(instance_report.VolumeId.unique())

#passing this to get Volume  information.

# To get IOPS and SIZE for the associated volumes. This will help in reviewing the IOPS asscoated to particular volume.
volumetypes = ['gp2']

response = ec2.describe_volumes(

    Filters=[
        {
            'Name': 'volume-type',
            'Values': volumetypes,
        },

    ], VolumeIds=list(instance_report.VolumeId.unique())
)
report=[]
for volume in response.get("Volumes"):
    if not volume.get("Iops") is None:
        for attach in volume.get("Attachments"):
            InstanceID = attach.get("InstanceId")

        #            if not len(volume.get("Tags")) == 0:
        #                print((next(tag for tag in volume.get("Tags") if tag["Key"] == "Owner")))
        #            else:
        #                print('Owner is not defined')
        VolumeId = attach.get("VolumeId")
        # print(VolumeId)
        row = [VolumeId, volume.get("Size"), volume.get("Iops"), volume.get("VolumeType"), InstanceID]
        report.append(row)





ebs_volume_info = pd.DataFrame(report,columns=['VolumeId', 'Size', 'Iops', 'VolumeType', 'InstanceID'])

print("Volumes and their IOPS details:")
print("\n")
print(ebs_volume_info.sort_values(by=['Iops', 'Size'], ascending=False))
print("\n")


print("Volumes having more IOPS defined :")
print("\n")
print(ebs_volume_info[(ebs_volume_info.Iops > 3*ebs_volume_info.Size )])
print("\n")

all_vol_metric_data=[]
clw=boto3.client('cloudwatch')
# cloud watch metric defination.
for uniq_vol in list(instance_report.VolumeId.unique()):
    vol_metric_data = collect_metrics_ebs_volume('vol-01056d0b796108524', clw, startdate, enddate)
    all_vol_metric_data.append(vol_metric_data)



mpd=pd.DataFrame(all_vol_metric_data,columns=["VolumeID","timestamp","TotalIOPSsec"])

print("Max IOPS obsereved per volume during the given datetime intervel: ")

print(mpd.groupby("VolumeID").max()["TotalIOPSsec"])

# response4 = clw.get_metric_statistics(
#     Namespace='AWS/EBS',
#     MetricName='VolumeReadOps',
#     Dimensions=[
#         {
#             'Name': 'VolumeId',
#             'Value': 'vol-01056d0b796108524'
#         },
#     ],
#     StartTime=datetime.datetime(2019, 6, 21),
#     EndTime=datetime.datetime(2019, 6, 22),
#     Period=300,
#     Statistics=['Sum',]
#
# )
#
# for sample in response4.get("Datapoints"):
#     print(sample.get("Sum"))
# response4 = clw.get_metric_statistics(
#     Namespace='AWS/EBS',
#     MetricName='VolumeWriteOps',
#     Dimensions=[
#         {
#             'Name': 'VolumeId',
#             'Value': 'vol-01056d0b796108524'
#         },
#     ],
#     StartTime=datetime.datetime(2019, 6, 21),
#     EndTime=datetime.datetime(2019, 6, 22),
#     Period=300,
#     Statistics=['Sum',]
#
# )
# for sample in response4.get("Datapoints"):
#     print(sample.get("Sum"))
