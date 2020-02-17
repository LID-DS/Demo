
import threading
import json
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from read_write_syscalls import SysdigHandling

"""
initiate websocket
react app asks for updates of statistics and IDS alarms
"""
def webserver():
    sysdig_handling = SysdigHandling()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app, cors_allowed_origins = '*')
    update_thread = threading.Thread(target=statistic_update, args=([socketio, sysdig_handling]))
    update_thread.start()

    @app.route('/')
    def index():
        return render_template('index.html')

    def messageReceived(methods = ['GET','POST']):
        print('message recieved')

    """
    Client can ask for newest stats
    with message "sum":
    send sum
    """
    @socketio.on('get stats')
    def handle_message(message):
        print('recieved message: ' + message)
        if message == 'sum':
            print('send sum')
            emit('stats_sum', json.loads('{"sum":' + str(sysdig_handling.statistic.get_sum()) + '}')) #sysdig_handling.sum})

    @socketio.on('my event')
    def handle_my_custom_event(json, methods=['GET', 'POST']):
        print('received my event: ' + str(json))
        emit('my response')
    socketio.run(app)

def statistic_update(socketio, sysdig_handling):
    """
    send React new statistic
    """
    delay = 1
    while True :
        socketio.emit('stats_sum', json.loads('{"sum":' + str(sysdig_handling.statistic.get_calls_per_minute()) + '}')) 
        time.sleep(delay)


if __name__ == "__main__":
    webserver()
