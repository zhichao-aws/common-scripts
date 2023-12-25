import boto3
from utils import store_json

def get_ImageId(configs):
    if "ImageId" in configs:
        return configs["ImageId"]
    client = boto3.client('ec2', region_name=configs["RegionInfo"]["RegionName"])
    filters = [
        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*']},
        {'Name': 'state', 'Values': ['available']},
        {'Name': 'architecture', 'Values': ['x86_64']},
    ]

    response = client.describe_images(Filters=filters, Owners=['099720109477'])  # Ubuntu's owner ID
    images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
    return images[0]["ImageId"]

def create_instances(configs):
    ec2_res = boto3.resource('ec2',region_name=configs["RegionInfo"]["RegionName"])
    instance_ids = dict()
    ImageId = get_ImageId(configs)

    for instance_type,instance_count in configs["InstanceMap"].items():    
        instances = ec2_res.create_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'VolumeSize': configs["VolumeSize"],
                    },
                },
            ],
            ImageId=ImageId,
            MinCount=instance_count,
            MaxCount=instance_count,
            InstanceType=instance_type,
            KeyName=configs["RegionInfo"]["KeyName"],
            SecurityGroupIds=configs["SecurityGroupIds"],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': configs["Tags"]
                },
            ],
            IamInstanceProfile=configs["IamInstanceProfile"]
        )
        instance_ids[instance_type]=[instance.id for instance in instances]
        print("allocate %d instances of type %s"%(instance_count,instance_type))
        
    store_json(instance_ids,"ids",configs)