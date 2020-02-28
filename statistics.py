import collections

class Statistic:

    def __init__(self):
        self.syscall_sum = 0
        self.start_time = 0
        self.calls_per_minute = 0
        self.bucket_counter = 0
        self.bucket_update_delay = 1000
        self.deque_syscall_per_second = collections.deque()
        self.syscall_type_dict_bucket = {}
        self.syscall_type_dict = {}
        self.ids_score = 0

    def update_statistic(self, syscall, ids_score):
        self.calc_sum()
        #self.calc_syscall_type_distribution()
        self.calc_calls_per_minute(syscall)
        self.ids_score = ids_score

    def calc_syscall_type_distribution(self):
        """
        scan through deque and read syscall type dictionary
        sum occurences of each syscall and return summed dictionary 
        """
        self.syscall_type_dict = {}
        for syscall in self.deque_syscall_per_second:
            syscall_type_dict = syscall[2]
            for syscall_type in syscall_type_dict:
                if syscall_type in self.syscall_type_dict:
                    self.syscall_type_dict[syscall_type] += syscall_type_dict[syscall_type]
                else:
                    self.syscall_type_dict[syscall_type] = syscall_type_dict[syscall_type]
        return self.syscall_type_dict 

    def get_syscall_distribution(self):
        return self.syscall_type_dict
        
    def calc_sum(self):
        self.syscall_sum += 1
        return None

    def get_sum(self):
        return self.syscall_sum

    def calc_calls_per_minute(self,syscall):
        rawtime_of_syscall = syscall[1]
        syscall_type = syscall[6]
        syscall_type_dict = {}
        if self.start_time == 0:
            self.start_time = int(rawtime_of_syscall)

        # count all syscall occurences per bucket_update_delay
        # additionaly count different types of calls
        if int(rawtime_of_syscall) - self.start_time < self.bucket_update_delay:
            if self.bucket_counter == 0:
                start_timestamp = int(rawtime_of_syscall)
            self.bucket_counter += 1
            #TODO ADD SYSCALL TYPE CORRECT NOT ONE PER BUCKET
            # add entry to dictionary, count type of systemcall to bucket information
            if syscall_type in syscall_type_dict:
                self.syscall_type_dict_bucket[syscall_type] += 1
            else:
                self.syscall_type_dict_bucket[syscall_type] = 1


        # add newest bucket to deque and pop oldest if more than 60 entries
        else:
            deque_entry = [self.bucket_counter, self.start_time, self.syscall_type_dict_bucket]
            self.deque_syscall_per_second.append(deque_entry)
            if len(self.deque_syscall_per_second) > 1 :
                dropped = self.deque_syscall_per_second.popleft()
            self.bucket_counter = 0
            self.syscall_type_dict_bucket = {}
            self.start_time = int(rawtime_of_syscall)
        
    def get_calls_per_second(self):
        #current_time = int(round(time.time() * 1000))
        #last_bucket_time = current_time 
        syscall_counter = 0
        for syscall in self.deque_syscall_per_second:
            syscall_counter += syscall[0]
        return syscall_counter
    

