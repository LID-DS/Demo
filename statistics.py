import collections

class Statistic:

    def __init__(self):
        self.syscall_sum = 0
        self.start_time = 0
        self.calls_per_minute = 0
        self.bucket_counter = 0
        self.bucket_update_delay = 1000
        self.deque_syscall_per_second = collections.deque()

    def update_statistic(self, syscall):
        self.calc_sum()
        self.calc_calls_per_minute(syscall[1])

    def calc_sum(self):
        self.syscall_sum += 1
        return None

    def get_sum(self):
        return self.syscall_sum

    def get_calls_per_minute():
        current_time = int(round(time.time() * 1000))
        last_bucket_time = current_time 
        syscall_counter = 0
        print(len(self.deque_syscall_per_second))
        return syscall_counter

    def calc_calls_per_minute(self,rawtime_of_syscall):
        if self.start_time == 0:
            self.start_time = int(rawtime_of_syscall)

        if int(rawtime_of_syscall) - self.start_time < self.bucket_update_delay:
            if self.bucket_counter == 0:
                start_timestamp = int(rawtime_of_syscall)
            self.bucket_counter += 1

        else:
            deque_entry = [self.bucket_counter, self.start_time]
            self.deque_syscall_per_second.append(deque_entry)
            self.bucket_counter = 0
            self.start_time = int(rawtime_of_syscall)
        
