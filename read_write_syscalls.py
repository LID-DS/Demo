from contextlib import contextmanager
import subprocess
import collections
import threading
import time
import psutil

IN_DOCKER=False

class SysdigHandling:

    """
    on initiation:
        start two threads for reading syscalls
        first reads syscalls with sysdig and writes them to deque
                with attributes:
                    containerID
                    rawtime
                    latency
                    process name
                    threadID
                    direction: > start syscall with with params listed below
                               < return
                    syscall type
                    arguments of syscall as list

            second thread reads syscalls from deque
        start a deque to write systemcalls to
        create data_handling class - where calculations on syscalls are made
    """
    def __init__(self, data_handling):
        # Initiate syscall deque
        self.deque_syscall = collections.deque()
        # Initiate write deque thread
        self.write_thread = threading.Thread(
                target=self.write_syscalls, args=())
        self.write_thread.start()
        # Initiate read deque thread
        self.read_thread = threading.Thread(
                target=self.read_syscall, args=([]))
        self.read_thread.start()
        # Initiate data_handling
        self.data_handling = data_handling

    @contextmanager
    def start_sysdig_and_read_data(self):
        """
        start sysdig process on docker container with params:
            container_ID, raw_time, latency, process_name,
            thread_ID, direction, syscall_type, syscall_arguments
            or start only listening node process
        """
        self.sysdig_process = None
        try:
            if IN_DOCKER:
                print("Sysdig monitoring docker container")
                # collect information for all containers except host
                sensor_command_line = ['sudo', '/usr/bin/sysdig',
                                       # '--unbuffered',
                                        '-p %container.id %evt.rawtime %evt.latency %proc.name %thread.tid %evt.dir %syscall.type %evt.args',
                                       'container.id!=host and syscall.type!=container']
            else:
                print("Sysdig monitoring Node App")
                # listen node process
                sensor_command_line = ['sudo', '/usr/bin/sysdig',
                        'proc.name=node',
                        '-p %evt.rawtime %evt.latency %proc.name %thread.tid %evt.dir %syscall.type %evt.args']
            self.sysdig_process = subprocess.Popen(
                    sensor_command_line,
                    stdout=subprocess.PIPE,
                    encoding="utf-8")
            yield self.sysdig_process
        finally:
            self.sysdig_process.terminate()
            self.sysdig_process.kill()

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
        parsed_syscall = [8]
        if IN_DOCKER:
            parsed_syscall[0:7] = syscall[0:7]
        else: 
            parsed_syscall[0] = 0  
            parsed_syscall[1:7] = syscall[0:6]
        list_of_arguments = syscall[7:]
        parsed_syscall.append(list_of_arguments)
        return parsed_syscall

    def write_syscalls(self):
        """
        get read system calls from sysdig subprocess call
        write system calls in deque
        """
        with self.start_sysdig_and_read_data() as sysdig_out:
            for line in sysdig_out.stdout:
                self.deque_syscall.append(self.syscall_parser(line))

    def read_syscall(self):
        """
        read system calls from deque
        if deque not empty send syscall to data_handlings
        """
        while True:
            # check if deque is empty
            if self.deque_syscall:
                syscall = self.deque_syscall.pop()
                # send to data_handling
                self.data_handling.update_statistic(syscall)
            else:
                time.sleep(0.1)

    def stop_process(self):
        """
        stop sysdig subprocess
        """
        for proc in psutil.process_iter():
            if proc.name() == "sysdig":
                print("killed")
                proc.kill()
