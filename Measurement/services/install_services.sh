#!/bin/bash
# Don't forget to make this file executable first:
# chmod a+rx 

# copy the service unit files to systemd
sudo cp *.service /lib/systemd/system/

# tell systemd to recognize our service
sudo systemctl daemon-reload

# tell systemd that we want our service to start on boot
for file in *.service
do
    echo enabling ${file} 
    sudo systemctl enable ${file}
    
done

