from contextlib import contextmanager
import subprocess 
import collections
from rethinkdb import RethinkDB
import time
import threading
import data_handling as DataHandling


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
        
    @contextmanager
    def start_sysdig_and_read_data(self):
        """
        start sysdig process with params: container_ID, raw_time, latency, process_name, thread_ID, direction, syscall_type, syscall_arguments
        """
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

    def syscall_parser(self, syscall):
        # create list of information contained in syscall
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

    def write_syscalls(self):    
        print("writing")
        with self.start_sysdig_and_read_data() as sysdig_out:
            for line in sysdig_out.stdout:
                self.deque_syscall.append(self.syscall_parser(line))

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
                #print("Read syscall: ", self.deque_syscall.popleft())
                #print("Entries left: ", len(self.deque_syscall))
            #else:
            #    print("No syscalls to read")

    def calc_new_statistic(self):
        #tmp_count = rethink_db.table("statistics").filter
        #rethink_db.table("statistics").update({"sum": global_test_counter})
        sum_syscalls = self.data_handling.get_sum() 
        print("calc")
        print(sum_syscalls)
        self.data_handling.update_statistics(sum_syscalls + 1)

        return None
    
if __name__ == "__main__":
    sysdig_handling = SysdigHandling()
    print("initialize threads")
    print("start write")
    print("start read")
