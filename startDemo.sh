#!/bin/bash


#enabling docker to run without sudo rights
#sudo groupadd docker &&
#sudo usermod -aG docker $USER &&   
#newgrp docker

#||
#enabling sysdig to run without sudo rights
sudo groupadd sysdig &&
sudo usermod -aG sysdig $USER &&
newgrp sysdig &&

echo "%sysdig ALL= /usr/bin/sysdig" | sudo EDITOR='tee -a' visudo

#||
# tmux session with prepared config which starts:
#   docker juice shop
#   react app
#   webserver.py for syscall analysis
#   userAction.py for automated traffic on juice shop

tmuxp load startDemo.yaml
