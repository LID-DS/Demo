#!/bin/bash

#Things to install
#npm -version
#6.14.1
#node -version
#v8.10.0
npm install

#install pip
sudo apt install python3-pip

#python requirements
pip3 install -r requirements.txt

#sysdig
curl -s https://s3.amazonaws.com/download.draios.com/stable/install-sysdig | sudo bash

#for selenium
#download geckodriver and mv to /usr/bin
curl -s https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux32.tar.gz | tar -xzvf

#geckodriver-v0.26.0-linux64.tar.gz

sudo mv ~/Downloads/geckodriver /usr/bin
