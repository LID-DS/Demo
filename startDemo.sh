#!/bin/bash

#install prequesites for downloading and installing needed features
sudo apt update
sudo apt install curl -y
sudo apt install python3-pip -y


#Frontend
#React
# install nvm
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.35.2/install.sh | bash
#TODO restart terminal so command nvm is usable
#try
source ~/.bashrc
# install node and matching npm via nvm
nvm install 12.6
#install demo-app dependencies
npm install --prefix demo-app/
#Webshop
sudo apt install docker.io -y
#allow docker to run as sudo without entering password
echo 'demo ALL=(ALL) NOPASSWD: /usr/bin/docker' | sudo tee -a /etc/sudoers
#sudo apt install nvm

#Backend
#install python dependencies
cd ~/Documents/Demo/
pip3 install -r requirements.txt
#install sysdig
curl -s https://s3.amazonaws.com/download.draios.com/stable/install-sysdig | sudo bash

#UserActions
mkdir Downloads && cd Downloads
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb 
sudo apt install ./google-chrome-stable_current_amd64.deb -y
cd ..
sudo apt install chromium-chromedriver -y

sudo apt update

sudo apt install tmux -y
sudo apt install tmuxp -y

# tmux session with prepared config which starts:
#   docker juice shop
#   react app
#   webserver.py for syscall analysis
#   userAction.py for automated traffic on juice shop

#TODO userAction wait until page is reachable
tmuxp load startDemo.yaml
