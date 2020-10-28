import threading
import time
import logging
import subprocess
import psutil

from flask import Flask
from flask_socketio import SocketIO, emit

from data_handling import DataHandling
from Automated_Users.userAction_headless import UserManager
from Automated_Users.Attacks.attack_manager import AttackManager

IN_DOCKER = False


class Backend:

    def __init__(self):
        """
        if not run in docker start webshop
        and save PID of started npm processes
        """
        if not IN_DOCKER:
            npm_pid = self.start_webshop()
            webshop_pid = self.get_child_pid(npm_pid)
            print(webshop_pid)
        else:
            webshop_pid = None
        """
        setup data_handling to 
            setup of sysdig handling to record system calls for specified pid
            compute syscall statistics
            evaluate syscalls with IDS
        """
        self.data_handling = DataHandling(pid=webshop_pid)
        """
        initialize socket
        """
        self.app = None
        self.initialize_socket()
        """
        start repetetivly collect data of data_handling in new thread
        """
        update_thread = threading.Thread(
                target=self.data_update,
                args=())
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
        start socket
        """
        self.socketio.run(self.app)

    def initialize_socket(self):
        """
        initiate websocket
        enable handling of
        -> retraining of model
        -> loading model
        -> saving model
        -> access user actions
          -> including attacks
        """
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        self.app = Flask(__name__)
        self.app.logger.disabled = True

        self.app.config['SECRET_KEY'] = 'secret!'
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')

        @self.socketio.on('choosing ids')
        def handle_message(json, methods=['GET','POST']):
            self.data_handling.ids_wrapper.set_active_ids(json)

        @self.socketio.on('training update')
        def handle_message(json, methods=['GET', 'POST']):
            self.data_handling.ids_wrapper.init_stide(training_size=int(str(json)))

        @self.socketio.on('load model')
        def handle_message(json, methods=['GET', 'POST']):
            """
            if 'load model' was received from frontend
            run _load_model of DemoStide
            creates now instance of ids
            reinitialize data_handling and with new ids
            reinitialize sysdig_handling with new data_handling instance
            """
            #TODO multiple models returned if multiple active
            self.data_handling.ids_wrapper.load_active_models()

        @self.socketio.on('save model')
        def handle_message(json, methods=['GET', 'POST']):
            """
            if 'save model' was received from frontend,
            save ids model
            """
            self.data_handling.ids_wrapper.save_active_model()

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
            elif str(json) == 'remove':
                self.userManager.remove_user()
            elif str(json) == 'add_head':
                self.userManager.add_user(visible=True)
            elif str(json) == 'start_training':
                self.userManager.start_training_sequence()
            elif str(json) == 'stop_training':
                self.userManager.stop_training_sequence()

        @self.socketio.on('start attack')
        def handle_message(json, methods=['GET', 'POST']):
            """
            start sql injection
            """
            print("attack input")
            if (str(json) == 'sql' or str(json) == 'try hard sql'):
                self.attackManager.run_sql_injection(str(json))
            elif str(json) == 'false jwt login':
                self.attackManager.run_false_jwt_login()
            elif str(json) == 'xss simple':
                self.attackManager.run_xss(str(json))
            elif str(json) == 'xss advanced':
                self.attackManager.run_xss(str(json))
            elif str(json) == 'data exposure simple':
                exposed_file_path = "/ftp/acquisitions.md"
                self.attackManager.run_sensitive_data_exposure(
                        exposed_file_path)
            elif str(json) == 'data exposure advanced':
                exposed_file_path = "/support/logs"
                self.attackManager.run_sensitive_data_exposure(
                        exposed_file_path)
            elif str(json) == 'remote code execution':
                self.attackManager.run_remote_code_execution()
            elif str(json) == 'file override':
                self.attackManager.run_file_override()

        @self.socketio.on('enum')
        def handle_message(json, methods=['GET', 'POST']):
            """
            start enumeration with dirb
            """
            self.attackManager.run_enum()
            self.socketio.emit('enum', "done")

    def data_update(self):
        """
        collect data of syscall_data_handling and ids
        send collected data with delay of delay = 1 seconds to react frontend
        """
        #Structure:
        stats = {
            'time': 0,
            'syscall_info': {
                'sum_all': 0,
                'sum_second': 0,
                'distribution_all': {},
                'distribution_second': {}
            },
            'ids_info': {
                'stide': {
                    'active': bool,
                    'score': 0,
                    'state': 0,
                    'training_size': 0,
                    'current_ngrams': [],
                    'top_ngrams': [],
                    'int_to_sys': {}
                }
            },
            'userAction': {
                'userCount': 0,
                'sequence_running': False
            },
            'analysis': {
                'alarm_content': ""
            }
        }
        delay = 1
        # TODO time steps more sophisticated
        time_since_start = 0
        stats = {}
        while True:
            try:
                try:
                    # time_first_call
                    stats['time'] = time_since_start
                except Exception:
                    print("get time failed")
                try:
                    stats['syscall_info'] = {
                        'sum': str(self.data_handling.get_sum()),
                        'sum_second': self.data_handling.get_calls_per_second(),
                        'distribution_all': self.data_handling.get_syscall_type_distribution(),
                        'distribution_second': self.data_handling.get_syscall_type_distribution_second()
                    }
                except Exception:
                    print("Systemcall info failed!")
                try:
                    if self.data_handling.ids_wrapper.active_ids["stide"] is not None:
                        stats['ids_info'] = {
                            'stide': {
                                'active': True,
                                'score': self.data_handling.ids_wrapper.get_ids_score_last_second(),
                                'state': self.data_handling.ids_info['stide']['state'],
                                'training_size': self.data_handling.ids_info['stide']['training_size'],
                                'current_ngrams': 
                                    self.data_handling.ids_info['stide']['current_ngrams'],
                                'top_ngrams': 
                                    self.data_handling.get_top_ngrams(),
                                'int_to_sys': 
                                    self.data_handling.get_int_to_sys()
                            }
                        }
                    else:
                        stats['ids_info']['stide'] = {
                            'active': False
                        }
                except Exception:
                    print("IDS info failed!")
                try:
                    stats['analysis'] = {
                        'alarm_content': 
                            self.data_handling.get_alarm_content()
                    }
                except Exception:
                    print("Analysis info failed!")
                try:
                    if self.userManager.sequence_running:
                        sequence_running = True
                    else:
                        sequence_running = False
                    stats['userAction'] = {
                        'userCount': len(self.userManager.active_users) +
                                     len(self.userManager.removing_users),
                        'training_running': sequence_running
                    }
                except Exception:
                    print("userCount info failed")

                time_since_start += 1
                self.socketio.emit('stats', stats)
                time.sleep(delay)

            except Exception:
                print("Error building stats")
                print(stats)

    def retrain_ids(self, training_size=None, trained_model=None):
        """
        retrain ids
            reinitialize data_handling with ids
            and start new sysdig process with new statistc
        :params training_size
        :params trained_model
        """
        if trained_model is None:
            self.data_handling.ids_wrapper.init_stide(
                    training_size=training_size)
        else:
            self.data_handling.ids_wrapper.init_stide(
                    trained_model=trained_model)

    def start_webshop(self):
        """
        start webshop
        :return : pid of npm process
        """
        npm_subprocess = subprocess.Popen(
                ['npm', 'start'],
                cwd="../Juice_Shop_Source/juice-shop/")
        time.sleep(5)
        return npm_subprocess.pid

    def get_child_pid(self, pid):
        """
        Process tree:
        npm
        ---sh
        ------node
        :params: pid of npm process
        :returns: pid of node process
        """
        sh_process = psutil.Process(pid).children()[0]
        webshop_pid = sh_process.children()[0].pid
        return webshop_pid


if __name__ == "__main__":
    IDS = Backend()
