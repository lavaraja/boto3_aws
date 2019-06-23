import boto3
import datetime
def collect_metrics_ebs_volume(volid,connectionobject,startdate,enddate):
    # spliiting date as there will be only 1440 datapoints in a single API call
    metric_data=[]
    split=enddate-startdate
    if(split<=datetime.timedelta(0)):

        print("Start time cannot be greater than or equl to end time")
        exit(1)

    intervel=int((split.days)/5)
    if intervel==0:
        intervel=1

    print("intervel")
    for x in range(intervel):
        print("entered the loop")
        if x==intervel-1:
            enddate=startdate+(datetime.timedelta(split.days%5))
        else:
            enddate=startdate+datetime.timedelta(5)
        print(enddate)

        response1 = connectionobject.get_metric_statistics(
            Namespace='AWS/EBS',
            MetricName='VolumeReadOps',
            Dimensions=[
                {
                    'Name': 'VolumeId',
                    'Value': volid
                },
            ],
            StartTime=startdate,
            EndTime=enddate,
            Period=300,
            Statistics=['Sum', ]

        )

        response2 = connectionobject.get_metric_statistics(
            Namespace='AWS/EBS',
            MetricName='VolumeWriteOps',
            Dimensions=[
                {
                    'Name': 'VolumeId',
                    'Value': volid
                },
            ],
            StartTime=startdate,
            EndTime=enddate,
            Period=300,
            Statistics=['Sum', ]

        )
        # for debug purpose

        print(response2)
        print(response1)
        startdate = enddate
        for x,y in zip(response2.get("Datapoints"),response1.get("Datapoints")):
            tmprow=[volid,x.get("Timestamp"),(x.get("Sum")+y.get("Sum"))/300]
            metric_data.append(tmprow)
            print(x.get("Timestamp"))
            print(x.get("Sum"))
            #print(y.get("Sum"))
    return metric_data

        # for sample in response2.get("Datapoints"):
        #
        #     print(sample.get("Sum"))
        #
        # for sample in response1.get("Datapoints"):
        #     print(sample.get("Sum"))


