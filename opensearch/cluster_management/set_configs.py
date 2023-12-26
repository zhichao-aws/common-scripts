import os
import boto3
import subprocess

from utils import load_json,get_instances_info, run_commands_on_dns

def get_memory(client,instance_type):
    memory = client.describe_instance_types(InstanceTypes=[instance_type])["InstanceTypes"][0]["MemoryInfo"]["SizeInMiB"]
    memory = int(memory/1024)//2
    return memory

def get_jvm_file(new_memory, configs):
    target_path = os.path.join(configs["store_dir"],configs["identifier"]+".jvm.options")
    with open('jvm.options.bak', 'r') as jvm_file:
        jvm_options = jvm_file.read()
        allocate_memory_str = str(int(new_memory)) + 'g'
        jvm_options = jvm_options.replace('-Xms1g', '-Xms' + allocate_memory_str)
        jvm_options = jvm_options.replace('-Xmx1g', '-Xmx' + allocate_memory_str)
        with open(target_path, 'w') as tmp_jvm:
            tmp_jvm.write(jvm_options)
    return target_path

def get_yml_file(manager_ip,node_count,configs):
    target_path = os.path.join(configs["store_dir"],configs["identifier"]+".opensearch.yml")
    with open('opensearch.yml', 'r') as yml_file:
        content = yml_file.read()
        content = content.replace("cluster.initial_cluster_manager_nodes: []",
                                 f"""cluster.initial_cluster_manager_nodes: ["{manager_ip}"]""")
        content = content.replace("discovery.seed_hosts: []",
                                 f"""discovery.seed_hosts: ["{manager_ip}.{configs["RegionInfo"]["RegionName"]}.compute.internal"]""")
        content = content.replace("node.max_local_storage_nodes: 1",
                                 f"""node.max_local_storage_nodes: {str(node_count)}""")
        with open(target_path, 'w') as f:
            f.write(content)
    return target_path

async def set_configs(configs):
    ids = load_json("ids",configs)
    client = boto3.client("ec2", region_name=configs["RegionInfo"]["RegionName"])
    manager_ip = get_instances_info(list(ids.values())[0],configs)["PrivateIpAddress"][0]
    manager_ip = manager_ip.replace(".","-")
    node_count = sum(map(len,ids.values()))

    yml_fp = get_yml_file(f"ip-{manager_ip}",node_count,configs)

    for instance_type, instance_ids in ids.items():
        max_mem = configs.get("max_mem",1e6)
        memory = get_memory(client,instance_type)
        jvm_fp = get_jvm_file(min(max_mem,memory),configs)
        
        info = get_instances_info(instance_ids,configs)
        print(info)
        
        commands = [f"""
                    scp -i /Users/zhichaog/.ssh/{configs["RegionInfo"]["KeyName"]+".pem"} {yml_fp} ubuntu@{dns}:/home/ubuntu/{configs["cluster_node_dir"]}/config/opensearch.yml
                    scp -i /Users/zhichaog/.ssh/{configs["RegionInfo"]["KeyName"]+".pem"} {jvm_fp} ubuntu@{dns}:/home/ubuntu/{configs["cluster_node_dir"]}/config/jvm.options
                    """ for dns in info["PublicDnsName"]]
        await run_commands_on_dns(commands,info["PublicDnsName"])