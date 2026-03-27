sudo cp minecraft-admin.service /etc/systemd/system

sudo systemctl start minecraft-admin
sudo systemctl enable minecraft-admin

journalctl -u minecraft-admin -f