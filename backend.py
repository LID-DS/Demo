import threading
import json
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import datetime

from statistics import Statistic
from read_write_syscalls import SysdigHandling
from demo_model_stide import DemoModelStide
from Automated_Users.userAction_headless import User, UserManager
from Automated_Users.Attacks.attack_manager import AttackManager


class Backend:

    def __init__(self):

        """
        setup statistic to compute syscall statistics and evaluate syscalls with IDS
        provides statistics of syscall an analysation of ids
        """
        self.statistic = Statistic()
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
        enable controlling of automated user actions
        """ 
        self.userManager = UserManager()
        """ 
        enable controlling of automated user attacks 
        """ 
        self.attackManager = AttackManager()
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
            self.retrain_ids(int(str(json)))

        @self.socketio.on('load model')
        def handle_message(json, methods=['GET', 'POST']):
            """
            if 'load model' was received from frontend run _load_model of DemoStide
            creates now instance of ids
            reinitialize statistic and with new ids
            reinitialize sysdig_handling with new statistic instance 
            """
            trained_model = self.statistic.ids._load_model()
            self.retrain_ids(trained_model=trained_model)
            
            
        @self.socketio.on('save model')
        def handle_message(json, methods=['GET', 'POST']):
            """ 
            if 'save model' was received from frontend, save ids model
            """
            self.statistic.ids._save_model() 

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
                #while(not stopped_user.is_finished):
                #    time.sleep(0.1)
            if str(json) == 'add_head':
                self.userManager.add_user(visible=True)
            #send how many users are active to frontend
            self.socketio.emit('user action', len(self.userManager.active_users))

        @self.socketio.on('start attack')
        def handle_message(json, methods=['GET', 'POST']):
            """
            start sql injection
            """
            self.attackManager.run_sql_injection(str(json))
            

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
            try:
                stats['sum'] = str(self.statistic.get_sum())
                stats['calls_per_second'] = self.statistic.get_calls_per_second()
                stats['time'] = time_since_start # time_first_call
                stats['syscall_type_dict_second'] = self.statistic.get_syscall_type_distribution_second()
                stats['syscall_type_dict'] = self.statistic.get_syscall_type_distribution()
                stats['ids_info'] = {
                    'score': self.statistic.get_ids_score(),
                    'state': self.statistic.ids._model_state.value,
                    'training_size': self.statistic.ids_info['training_size'],
                    'current_ngrams': self.statistic.ids_info['current_ngrams'],
                    'top_ngrams': self.statistic.get_top_ngrams(),
                    'int_to_sys': self.statistic.get_int_to_sys()
                }
                time_since_start += 1
                self.socketio.emit('stats', stats)
                time.sleep(delay)

            except:
                print("Error building stats")


    def retrain_ids(self, training_size=None, trained_model=None):
        """
        retrain ids 
            reinitialize statistic with ids and start new sysdig process with new statistc
        :params training_size 
        :params trained_model
        """
        if trained_model == None:
            self.statistic.ids = DemoModelStide(training_size=training_size)
        else: 
            self.statistic.ids = DemoModelStide(trained_model=trained_model)
        

if __name__ == "__main__":
    IDS = Backend()
