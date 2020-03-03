import docker
import webserver

import os

#start container
os.system('sudo docker run -d vulhyb/mysql:5.5.23')

#start webserver
webserver.start()

#start react app
cmd = 'npm start --prefix demo-app/'
os.system(cmd)



