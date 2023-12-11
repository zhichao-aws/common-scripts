```
scp ~/Downloads/chronicled_2.0.1692.0_amd64.deb ubuntu@benchmark:/home/ubuntu/chronicled_2.0.1692.0_amd64.deb
sudo dpkg -i chronicled_2.0.1692.0_amd64.deb
systemctl list-units --type=service --state=running
```