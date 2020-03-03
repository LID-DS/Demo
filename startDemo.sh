#!/bin/bash

#start docker
#sudo docker run -d 'vulhub/mysql:5.5.23'
sudo docker run --rm -p 3000:3000 bkimminich/juice-shop

#start webserver
python3 webserver.py &

#start react application
npm start --prefix demo-app/

