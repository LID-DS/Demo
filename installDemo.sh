#!/bin/bash

#install prequesites for downloading and installing needed features
sudo apt update
sudo apt install curl -y
sudo apt install python3-pip -y


#Frontend
#React
# install nvm
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.35.3/install.sh | bash
#TODO restart terminal so command nvm is usable
#try
. ~/.nvm/nvm.sh
. ~/.profile
. ~/.bashrc
# install node and matching npm via nvm
nvm install 12.16.1
#install demo-app dependencies
npm install --prefix demo-app/
#Webshop
#Docker version
sudo apt install docker.io -y
#allow docker to run as sudo without entering password
echo '$USER ALL=(ALL) NOPASSWD: /usr/bin/docker' | sudo tee -a /etc/sudoers
#build from sources
mkdir Juice_Shop_Source
cd Juice_Shop_Source
git clone https://github.com/bkimminich/juice-shop.git
cd juice-shop
git fetch origin 99f93b44f61fba6d4428518231f36d41cc6cd760 
npm install -y

cd ../..
#Backend
#install python dependencies
pip3 install -r requirements.txt
#install sysdig
curl -s https://s3.amazonaws.com/download.draios.com/stable/install-sysdig | sudo bash
#dont ask for sudo password with sysdig
echo '$USER ALL=(ALL) NOPASSWD: /usr/bin/sysdig' | sudo tee -a /etc/sudoers
# TODO needed????
#dont ask for sudo password with python3 programs
echo '$USER ALL=(ALL) NOPASSWD: /usr/bin/python3' | sudo tee -a /etc/sudoers

#UserActions
#TODO update chromdriver download
mkdir Downloads && cd Downloads
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb 
sudo apt install ./google-chrome-stable_current_amd64.deb -y
cd ..
sudo apt install chromium-chromedriver -y
sudo apt install dirb

sudo apt install tmux
sudo apt install tmuxp

sudo apt update

sudo mkdir alarm_info/tracked_window
sudo mkdir alarm_info/raw_syscall
