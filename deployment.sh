#!/bin/bash
git pull


sudo systemctl restart tax_app.service
sudo systemctl restart nginx
echo "SUCCESSFULLY DEPLOYED"
