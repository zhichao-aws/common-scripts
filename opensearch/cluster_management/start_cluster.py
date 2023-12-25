import boto3
import subprocess

from utils import load_json,get_instances_info

def start_cluster(configs):
    ids = load_json("ids",configs)
    endpoints = []
    
    for instance_type, instance_ids in ids.items():
        info = get_instances_info(instance_ids,configs)
        print(info)
        endpoints += [f"https://{dns}:9200" for dns in info["PublicDnsName"]]
        for dns in info["PublicDnsName"]:
            command = f"""
            ssh -i /Users/zhichaog/.ssh/{configs["RegionInfo"]["KeyName"]+".pem"} ubuntu@{dns} << EOF
            cd /home/ubuntu/{configs["cluster_node_dir"]}
            pgrep -f opensearch | xargs kill -9
            sleep 10
            ls
            nohup sh opensearch-tar-install.sh > nohup.log 2>&1 &
            pgrep opensearch
            """
            res = subprocess.run(command, shell=True)
            print(f"finished for {dns}.",res)
            
    print(endpoints)