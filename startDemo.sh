#!/bin/bash

#start docker
sudo docker run -d 'vulhub/mysql:5.5.23'

#start webserver
python3 webserver.py &

#start react application
npm start --prefix demo-app/

