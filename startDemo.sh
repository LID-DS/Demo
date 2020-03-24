#!/bin/bash

#install prequesites for downloading and installing needed features
sudo apt update
sudo apt install git -y
sudo apt install curl -y
sudo apt install python3-pip -y


#Frontend
#React
# install nvm
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.35.2/install.s | bash
# install node and matching npm via nvm
nvm install v8.10.0
#Webshop
sudo apt install docker -y

#Backend
#install python dependencies
pip3 install -r requirements.txt
#install sysdig
curl -s https://s3.amazonaws.com/download.draios.com/stable/install-sysdig | sudo bash

#UserActions
mkdir Downloads && cd Downloads
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb 
sudo apt install ./Downloads/google-chrome-stable_current_amd64.deb -y
sudo apt install chromium-chromedriver -y

sudo apt update

# tmux session with prepared config which starts:
#   docker juice shop
#   react app
#   webserver.py for syscall analysis
#   userAction.py for automated traffic on juice shop

tmuxp load startDemo.yaml
