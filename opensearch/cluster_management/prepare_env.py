import boto3
import subprocess

from utils import load_json,get_instances_info

def prepare_env(configs):
    ids = load_json("ids",configs)
    client = boto3.client("ec2", region_name=configs["RegionInfo"]["RegionName"])
    
    for instance_type, instance_ids in ids.items():
        info = get_instances_info(instance_ids,configs)
        print(info)
        for dns in info["PublicDnsName"]:
            command = f"""
            ssh -o StrictHostKeyChecking=no -i /Users/zhichaog/.ssh/{configs["RegionInfo"]["KeyName"]+".pem"} ubuntu@{dns} << EOF
            sudo apt update -y > /dev/null
            sudo apt install awscli -y > /dev/null
            aws s3 cp s3://neural-sparse/2.12.0-SNAPSHOT.tar.gz 2.12.0-SNAPSHOT.tar.gz
            tar -xzvf 2.12.0-SNAPSHOT.tar.gz > /dev/null

            echo 'vm.max_map_count=262144' | sudo tee /etc/sysctl.conf
            sudo sysctl -p
            ls
            """
            res = subprocess.run(command, shell=True)
            print(f"finished for {dns}.",res)