import pdb
import threading
import json
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import datetime

from statistics import Statistic
from read_write_syscalls import SysdigHandling
import demo_model_stide
from Automated_Users.userAction_headless import User, UserManager


INITIAL_TRAINING_SIZE = 100000

class Backend:

    def __init__(self):

        """ 
        enable controlling of automated user actions
        """ 
        self.userManager = UserManager()
        print('added userManger')
        """
        setup IDS   
        """
        self.ids = demo_model_stide.DemoModelStide(training_size=INITIAL_TRAINING_SIZE)
        """
        setup statistic to compute syscall statistics and evaluate syscalls with IDS
        provides statistics of syscall an analysation of ids
        """
        self.statistic = Statistic(self.ids)
        """
        setup sysdig handling to record system calls and send calls to ids
        writes and reads queue in different threads and sends each syscall to statistic
        """
        self.sysdig_handling = SysdigHandling(self.statistic)
        self.start()
        """
        start repetetivly collecting data of statistic in new thread
        """
        update_thread = threading.Thread(target=self.data_update, args=())
        update_thread.start()
        """ 
        run socket
        """ 
        self.socketio.run(self.app)

    """
    initiate websocket
    """
    def start(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')

        @self.app.route('/')
        def index():
            return render_template('index.html')

        
        @self.socketio.on('training update')
        def handle_message(json, methods=['GET', 'POST']):
            print('Retrain with training size: ' + str(json))
            self.retrain_ids(int(str(json)))

        @self.socketio.on('user action')
        def handle_message(json, methods=['GET', 'POST']):
            if str(json) == 'add': 
                print('user action ' + str(json))
                self.userManager.add_user()
            if str(json) == 'remove': 
                print('user action ' + str(json))
                self.userManager.remove_user()
            #send how many users are active to frontend
            self.socketio.emit('user action', len(self.userManager.active_users))
            
            

    """
    collect data of syscall_statistics and ids
    send React collected data with delay of delay seconds
    """
    def data_update(self):
        delay = 1
        #TODO time steps more sophisticated
        time_since_start = 0
        stats = {}
        while True:
            stats['sum'] = str(self.statistic.get_sum())
            calls_per_second = self.statistic.get_calls_per_second()
            stats['calls_per_second'] = calls_per_second
            stats['time'] = time_since_start # time_first_call
            stats['syscall_type_dict'] = self.statistic.calc_syscall_type_distribution()
            stats['ids_info'] = {
                'score': self.statistic.get_ids_score(),
                'state': self.statistic.ids_info['state'],
                'training_size': self.statistic.ids_info['training_size'],
                'current_ngrams': self.statistic.ids_info['current_ngrams']
            }
            print(stats)
            time_since_start += 1
            self.socketio.emit('stats', stats)
            time.sleep(delay)

    """
    retrain ids with given training_size
    """
    def retrain_ids(self, training_size):
        self.ids = demo_model_stide.DemoModelStide(training_size=training_size)
        self.statistic = Statistic(self.ids)
        self.sysdig_handling = SysdigHandling(self.statistic)

if __name__ == "__main__":
    IDS = Backend()
