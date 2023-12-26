import os
import json
import boto3

import asyncio

async def run_command(command):
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    # Wait for the process to finish
    stdout, stderr = await process.communicate()

    # Check if the process has finished
    if process.returncode == 0:
        print(f"[Success]\nOutput:\n{stdout.decode()}")
    else:
        print(f"[Error]\nError Output:\n{stderr.decode()}")
        
async def run_commands_on_dns(commands,dns_list):
    processes = [run_command(command) for command,dns in zip(commands,dns_list)]
    result = await asyncio.gather(*processes)
    return result

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
    info = sorted(info, key=lambda x:x["InstanceId"])
    return {
        "PublicDnsName":[instance["PublicDnsName"] for instance in info],
        "PrivateIpAddress":[instance["PrivateIpAddress"] for instance in info]   
    }