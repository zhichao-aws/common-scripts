sudo apt update -y && sudo apt install awscli -y
aws s3 cp s3://neural-sparse/2.12.0-SNAPSHOT.tar.gz 2.12.0-SNAPSHOT.tar.gz
tar -xzvf 2.12.0-SNAPSHOT.tar.gz

echo 'vm.max_map_count=262144' | sudo tee /etc/sysctl.conf
sudo sysctl -p