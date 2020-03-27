import pdb
import threading
import json
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from read_write_syscalls import SysdigHandling
import datetime

"""
initiate websocket
react app asks for updates of statistics and IDS alarms
"""

def start():
    sysdig_handling = SysdigHandling()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app, cors_allowed_origins='*')
    update_thread = threading.Thread(target=statistic_update, args=([socketio, sysdig_handling]))
    update_thread.start()

    @app.route('/')
    def index():
        return render_template('index.html')

    def messageReceived(methods=['GET', 'POST']):
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
            emit('stats', json.loads('{"sum":' + str(sysdig_handling.statistic.get_sum()) + '}'))

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
    stats = {}
    while True:
        stats['sum'] = str(sysdig_handling.statistic.get_sum())
        calls_per_second = sysdig_handling.statistic.get_calls_per_second()
        stats['calls_per_second'] = calls_per_second
        stats['time'] = 0  # time_first_call
        stats['syscall_type_dict'] = sysdig_handling.statistic.calc_syscall_type_distribution()
        stats['ids_info'] = {
            'score': sysdig_handling.statistic.get_ids_score(),
            'state': sysdig_handling.statistic.ids_info['state'],
            'training_size': sysdig_handling.statistic.ids_info['training_size'],
            'current_ngrams': sysdig_handling.statistic.ids_info['current_ngrams']
        }

        print(stats['ids_info'])
        socketio.emit('stats', stats)
        time.sleep(delay)

def training_update(socketio):
    return 0
    #current_count of calls in trainingsphase
    #needed calls for training
    #training status
# Lernphase info
    # stand #systemcalls
    # vorgelerntes modell
# Automatisierte User per Knopfdruck starten
# Angriffe starten



if __name__ == "__main__":
    start()
