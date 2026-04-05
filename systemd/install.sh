sudo cp minecraft-admin.service /etc/systemd/system

sudo systemctl start minecraft-admin
sudo systemctl enable minecraft-admin

# sudo systemctl daemon-reexec
# sudo systemctl daemon-reload
# sudo systemctl restart minecraft-admin

journalctl -u minecraft-admin -f