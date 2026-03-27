#sudo rm /etc/nginx/sites-enabled/default

sudo cp minecraft-admin.conf /etc/nginx/sites-available

#sudo ln -s /etc/nginx/sites-available/minecraft-admin.conf /etc/nginx/sites-enabled/


sudo nginx -t
sudo systemctl reload nginx