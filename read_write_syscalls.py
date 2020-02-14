from contextlib import contextmanager
import subprocess 
import collections
from rethinkdb import RethinkDB
import time
import threading
import data_handling as DataHandling
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json

"""
initiate websocket
react app asks for updates of statistics and IDS alarms
"""
def webserver():
    sysdig_handling = SysdigHandling()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app, cors_allowed_origins = '*')

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
            emit('stats_sum', json.loads('{"sum":' + str(sysdig_handling.sum) + '}')) #sysdig_handling.sum})

    @socketio.on('my event')
    def handle_my_custom_event(json, methods=['GET', 'POST']):
        print('received my event: ' + str(json))
        emit('my response')


    socketio.run(app)

"""
on initiation:
    start two threads for reading syscalls 
        first thread reads syscalls with sysdig and writes them to deque
            with attributes:
                containerID
                rawtime
                latency
                process name
                threadID
                direction: > start syscall with with params listed below < return
                syscall type
                arguments of syscall as list

        second thread reads syscalls from deque
    start a deque to write systemcalls to
    create statistic class - where calculations on syscalls are made
"""
class SysdigHandling:

    write_thread = None
    read_thread = None 
    deque_syscall = None
    rethink_db = None
    data_handling = None

    def __init__(self):
        #Initiate syscall deque
        self.deque_syscall = collections.deque()
        #Initiate write deque thread
        self.write_thread = threading.Thread(target=self.write_syscalls, args=())
        self.write_thread.start()
        #Initiate read deque thread
        self.read_thread = threading.Thread(target=self.read_syscall, args=())
        self.read_thread.start()
        self.sum = 0
        
    """
    start sysdig process on docker container with params: container_ID, raw_time, latency, process_name, thread_ID, direction, syscall_type, syscall_arguments
    """
    @contextmanager
    def start_sysdig_and_read_data(self):
        sysdig_process = None
        try:
            print("starting sysdig")
            # collect information for all containers except host
            sensor_command_line = ['sudo','/usr/bin/sysdig', '--unbuffered',
                                '-p %container.id %evt.rawtime %evt.latency %proc.name %thread.tid %evt.dir %syscall.type %evt.args',
                                'container.id!=host and syscall.type!=container']
            sysdig_process = subprocess.Popen(sensor_command_line, stdout=subprocess.PIPE, encoding="utf-8")
            yield sysdig_process
        finally:
            sysdig_process.terminate()
            sysdig_process.kill()
    """
    create list of information contained in syscall
    """
    def syscall_parser(self, syscall):
        # list entries:
        # containerID
        # rawtime
        # latency
        # process name
        # threadID
        # direction: > start syscall with with params listed below < return
        # syscall type
        # arguments of syscall as list:
        syscall = syscall.split()
        parsed_syscall = []
        parsed_syscall[0:7] = syscall[0:7]
        list_of_arguments = syscall[7:]
        parsed_syscall.append(list_of_arguments)
        return parsed_syscall

    """
    get read system calls from sysdig subprocess call
    write system calls in deque 
    """ 
    def write_syscalls(self):    
        print("writing")
        with self.start_sysdig_and_read_data() as sysdig_out:
            for line in sysdig_out.stdout:
                self.deque_syscall.append(self.syscall_parser(line))

    """
    read system calls from deque
    if deque not empty send syscall to IDS and to statistics
    """
    def read_syscall(self):
        #Initiate DB
        self.data_handling = DataHandling.DataHandling()
        self.rethink_db = self.data_handling.get_table()
        while True:
            #check if deque is empty
            if self.deque_syscall:
                #send to IDS
                #send to statistics
                self.calc_new_statistic()
            else:
                print("No syscalls to read")
    """
    gathering function for all statistical analysis
    """ 
    def calc_new_statistic(self):
        self.calc_sum()
        
    """
    calculate sum of all system calls
    read current sum of system calls from rethinkdb
    """
    def calc_sum(self):
        #tmp_count = rethink_db.table("statistics").filter
        #rethink_db.table("statistics").update({"sum": global_test_counter})
        sum_syscalls = self.data_handling.get_sum() 
        self.data_handling.update_statistics(sum_syscalls + 1)
        self.sum = sum_syscalls + 1

        return None
    
if __name__ == "__main__":
    webserver()

