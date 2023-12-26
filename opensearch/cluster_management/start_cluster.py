import boto3
import subprocess

from utils import load_json,get_instances_info, run_commands_on_dns

async def start_cluster(configs):
    ids = load_json("ids",configs)
    endpoints = []
    
    for instance_type, instance_ids in ids.items():
        info = get_instances_info(instance_ids,configs)
        print(info)
        endpoints += [f"https://{dns}:9200" for dns in info["PublicDnsName"]]
        commands = [f"""
            ssh -o StrictHostKeyChecking=no -i /Users/zhichaog/.ssh/{configs["RegionInfo"]["KeyName"]+".pem"} ubuntu@{dns} << EOF
            cd /home/ubuntu/{configs["cluster_node_dir"]}
            if pgrep -f "opensearch" > /dev/null
            then
                echo "Process found. Attempting to kill..."
                # Kill the process
                pgrep -f "opensearch" | xargs kill -9
                echo "Process killed."
                sleep 10
            else
                echo "Process not found. Continuing..."
            fi
            nohup sh opensearch-tar-install.sh > nohup.log 2>&1 &
            sleep 2
            pgrep -f opensearch
            """ for dns in info["PublicDnsName"]]
        await run_commands_on_dns(commands,info["PublicDnsName"])
            
    print(endpoints)