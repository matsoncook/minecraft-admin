#sudo rm /etc/nginx/sites-enabled/default

sudo cp minecraft-admin.conf /etc/nginx/sites-enabled

#sudo ln -s /etc/nginx/sites-available/minecraft-admin.conf /etc/nginx/sites-enabled/

sudo chmod o+x /home/ubuntu
sudo chmod o+x /home/ubuntu/minecraft-admin
sudo chmod o+x /home/ubuntu/minecraft-admin/web
sudo chmod o+x /home/ubuntu/minecraft-admin/web/minecraft-admin
sudo chmod o+rx /home/ubuntu/minecraft-admin/web/minecraft-admin/dist
sudo chmod o+r /home/ubuntu/minecraft-admin/web/minecraft-admin/dist/index.html
sudo chmod -R o+r /home/ubuntu/minecraft-admin/web/minecraft-admin/dist/assets

sudo nginx -t
sudo systemctl reload nginx