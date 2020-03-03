import docker
import webserver

# start container
client = docker.from_env()
client.containers.run('vulhyb/mysql:5.5.23', detach=True)
webserver.start()
# start webserver
