```
sudo useradd —no-create-home nginx
```
```
sudo rm /etc/nginx/nginx.conf && sudo cp nginx.conf /etc/nginx/nginx.conf && sudo systemctl stop nginx && sudo systemctl start nginx


sudo systemctl start nginx
sudo nginx -s reload
```