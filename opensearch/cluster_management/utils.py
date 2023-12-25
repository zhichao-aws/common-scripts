import os
import json
import boto3

def get_store_path(configs,name):
    return os.path.join(configs["store_dir"],name)

def store_json(content,name,configs):
    path = get_store_path(configs,configs["identifier"]+"."+name)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(content,f)
        
def load_json(name,configs):
    path = get_store_path(configs,configs["identifier"]+"."+name)
    with open(path,encoding="utf-8") as f:
        return json.load(f)
    
def get_instances_info(InstanceIds, configs):
    client = boto3.client("ec2", region_name=configs["RegionInfo"]["RegionName"])
    info = client.describe_instances(InstanceIds=InstanceIds)["Reservations"][0]["Instances"]
    return {
        "PublicDnsName":[instance["PublicDnsName"] for instance in info],
        "PrivateIpAddress":[instance["PrivateIpAddress"] for instance in info]
        
    }