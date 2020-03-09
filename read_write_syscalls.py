from contextlib import contextmanager
import subprocess
import collections
import threading
from statistics import Statistic
import demo_model_stide
import time

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

    def __init__(self):
        # Initiate syscall deque
        self.deque_syscall = collections.deque()
        self.ids = demo_model_stide.DemoModelStide(training_size=10000)
        # Initiate write deque thread
        self.write_thread = threading.Thread(target=self.write_syscalls, args=())
        self.write_thread.start()
        # Initiate read deque thread
        self.read_thread = threading.Thread(target=self.read_syscall, args=([self.ids]))
        self.read_thread.start()
        # Initaite statistics
        self.statistic = Statistic()

    """
    start sysdig process on docker container with params: container_ID, raw_time, latency, process_name, thread_ID, direction, syscall_type, syscall_arguments
    """

    @contextmanager
    def start_sysdig_and_read_data(self):
        sysdig_process = None
        try:
            # collect information for all containers except host
            sensor_command_line = ['sudo', '/usr/bin/sysdig', #'--unbuffered',
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
        # 0 - containerID
        # 1 - rawtime
        # 2 - latency
        # 3 - process name
        # 4 - threadID
        # 5 - direction: > start syscall with with params listed below < return
        # 6 - syscall type
        # 7 - arguments of syscall as list:
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

    def read_syscall(self, ids):
        while True:
            # check if deque is empty
            if self.deque_syscall:
                syscall = self.deque_syscall.pop()
                # send to IDS
                result = ids.consume_system_call(syscall)
                # send to statistics
                self.statistic.update_statistic(syscall, result)
            else:
                time.sleep(0.1)
