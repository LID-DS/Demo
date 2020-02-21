import collections

class Statistic:

    def __init__(self):
        self.syscall_sum = 0
        self.start_time = 0
        self.calls_per_minute = 0
        self.bucket_counter = 0
        self.bucket_update_delay = 1000
        self.deque_syscall_per_second = collections.deque()
        self.syscall_type_dict = {}

    def update_statistic(self, syscall):
        self.calc_sum()
        self.calc_syscall_type_distribution(syscall)
        self.calc_calls_per_minute(syscall)

    def calc_syscall_type_distribution(self):
        #TODO sliding window implementation ?
        self.syscall_type_dict = {}
        for syscall in self.deque_syscall_per_second:
            syscall_type = syscall[2][6]
            if syscall_type in self.syscall_type_dict:
                self.syscall_type_dict[syscall_type] += 1
            else:
                self.syscall_type_dict[syscall_type] = 1
        
    def get_syscall_distribution(self):
        return self.syscall_type_dict
        
    def calc_sum(self):
        self.syscall_sum += 1
        return None

    def get_sum(self):
        return self.syscall_sum

    def calc_calls_per_minute(self,syscall):
        rawtime_of_syscall = syscall[1]
        if self.start_time == 0:
            self.start_time = int(rawtime_of_syscall)

        # count all syscall occurences per bucket_update_delay
        if int(rawtime_of_syscall) - self.start_time < self.bucket_update_delay:
            if self.bucket_counter == 0:
                start_timestamp = int(rawtime_of_syscall)
            self.bucket_counter += 1

        # add newest bucket to list and pop oldest if more than 60 entries
        else:
            deque_entry = [self.bucket_counter, self.start_time, syscall]
            self.deque_syscall_per_second.append(deque_entry)
            if len(self.deque_syscall_per_second) > 60:
                dropped = self.deque_syscall_per_second.popleft()
            self.bucket_counter = 0
            self.start_time = int(rawtime_of_syscall)
        
    def get_calls_per_minute(self):
        #current_time = int(round(time.time() * 1000))
        #last_bucket_time = current_time 
        syscall_counter = 0
        for syscall in self.deque_syscall_per_second:
            syscall_counter += syscall[0]
        return syscall_counter
    

