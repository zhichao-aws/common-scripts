import boto3
import subprocess

from utils import load_json,get_instances_info, run_commands_on_dns

async def prepare_env(configs):
    ids = load_json("ids",configs)
    client = boto3.client("ec2", region_name=configs["RegionInfo"]["RegionName"])
    
    for instance_type, instance_ids in ids.items():
        info = get_instances_info(instance_ids,configs)
        print(info)
        commands = [f"""
            ssh -o StrictHostKeyChecking=no -i /Users/zhichaog/.ssh/{configs["RegionInfo"]["KeyName"]+".pem"} ubuntu@{dns} << EOF
            wget {configs["released"]["url"]}
            tar -xzvf {configs["released"]["name"]} > /dev/null

            sudo swapoff -a
            echo 'vm.max_map_count=262144' | sudo tee /etc/sysctl.conf
            sudo sysctl -p
            ls
            
            cd /home/ubuntu/{configs["cluster_node_dir"]}
            nohup sh opensearch-tar-install.sh > nohup.log 2>&1 &
            sleep 10
            pgrep -f "opensearch" | xargs kill -9
            """ for dns in info["PublicDnsName"]]
        await run_commands_on_dns(commands,info["PublicDnsName"])