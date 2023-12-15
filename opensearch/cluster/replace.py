import os

ips=[
    "ec2-54-92-94-57.ap-northeast-1.compute.amazonaws.com",
    "ec2-43-206-193-232.ap-northeast-1.compute.amazonaws.com",
    "ec2-43-207-105-20.ap-northeast-1.compute.amazonaws.com"
]

print(",".join([ip+":9200" for ip in ips]))

for ip in ips:
    print("ssh -i /Users/zhichaog/.ssh/zhichao-tokyo.pem ubuntu@%s"%ip)
    command = "scp -i /Users/zhichaog/.ssh/zhichao-tokyo.pem opensearch.yml ubuntu@%s:/home/ubuntu/2.12.0-ARCHIVE/config/opensearch.yml"%ip
    print(command)
    os.system(command)