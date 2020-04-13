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


INITIAL_TRAINING_SIZE = 10

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

    def start(self):
        """
        initiate websocket
        enable handling of 
            retraining of model
            loading model
            saving model
        """
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')
        
        @self.socketio.on('training update')
        def handle_message(json, methods=['GET', 'POST']):
            print('Retrain with training size: ' + str(json))
            self.retrain_ids(int(str(json)))

        @self.socketio.on('load model')
        def handle_message(json, methods=['GET', 'POST']):
            """
            if 'load model' was received from frontend run _load_model of DemoStide
            creates now instance of ids
            reinitialize statistic and with new ids
            reinitialize sysdig_handling with new statistic instance 
            """
            self.ids = self.ids._load_model()
            self.statistic = Statistic(self.ids)
            self.sysdig_handling.stop_process()
            self.sysdig_handling = SysdigHandling(self.statistic)
            
        @self.socketio.on('save model')
        def handle_message(json, methods=['GET', 'POST']):
            """ 
            if 'save model' was received from frontend, save ids model
            """ 
            self.ids._save_model() 

        @self.socketio.on('user action')
        def handle_message(json, methods=['GET', 'POST']):
            """
            if 'user action' was received either:
                add automated user on webserver
                remove automated user 
            :params user_action ('add' or 'remove')
            :returns (emit) count of active users
            """
            if str(json) == 'add': 
                self.userManager.add_user()
            if str(json) == 'remove': 
                stopped_user = self.userManager.remove_user()
                while(not stopped_user.isfinished):
                    time.sleep(1)
            #send how many users are active to frontend
            self.socketio.emit('user action', len(self.userManager.active_users))

    def data_update(self):
        """
        collect data of syscall_statistics and ids
        send React collected data with delay of delay seconds
        """
        delay = 1
        #TODO time steps more sophisticated
        time_since_start = 0
        stats = {}
        while True:
            stats['sum'] = str(self.statistic.get_sum())
            calls_per_second = self.statistic.get_calls_per_second()
            stats['calls_per_second'] = calls_per_second
            stats['time'] = time_since_start # time_first_call
            stats['syscall_type_dict_second'] = self.statistic.get_syscall_type_distribution_second()
            stats['syscall_type_dict'] = self.statistic.get_syscall_type_distribution()
            stats['ids_info'] = {
                'score': self.statistic.get_ids_score(),
                'state': self.statistic.ids_info['state'],
                'training_size': self.statistic.ids_info['training_size'],
                'current_ngrams': self.statistic.ids_info['current_ngrams']
            }
            #print(stats)
            time_since_start += 1
            self.socketio.emit('stats', stats)
            time.sleep(delay)

    def retrain_ids(self, training_size, _normal_ngrams=None):
        """
        retrain ids 
            reinitialize statistic with ids and start new sysdig process with new statistc
        :params training_size
        :params _normal_ngrams
        """
        self.ids = demo_model_stide.DemoModelStide(training_size=training_size, _normal_ngrams=_normal_ngrams)
        self.statistic = Statistic(self.ids)
        self.sysdig_handling.stop_process()
        self.sysdig_handling = SysdigHandling(self.statistic)
        

if __name__ == "__main__":
    IDS = Backend()
