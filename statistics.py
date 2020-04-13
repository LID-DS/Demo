import collections
import pdb

MAX_BUCKETS = 1

class Statistic:
    

    def __init__(self, ids):
        self.syscall_sum = 0
        self.start_time = 0
        self.bucket_counter = 0
        self.bucket_update_delay = 1000
        self.deque_syscall_per_second = collections.deque()
        self.deque_syscall_type_per_second = collections.deque()
        self.syscall_type_dict_bucket = {}
        self.syscall_type_dict = {}
        self.syscall_type_dict_last_second = {} 
        self.ids = ids
        if (self.ids._model_state == 1):
            model_state = 1
        else:      
            model_state = 0
        self.ids_info = {
            'score': 0,
            'score_list': [],
            'state': model_state,
            'training_size': self.ids._training_size,
            'current_ngrams':self.ids._normal_ngrams['training_size'] 
        }

    def update_statistic(self, syscall):
        """
        received syscall from syscallhandling 
        calc new:
            sum of syscalls
            syscalls in last <bucket_size> (e.g 1 second)
            syscall distribution
            gather ids information 
                score
                state
                training size
                current seen ngrams
        """ 
        self.calc_sum()
        self.calc_calls_per_bucket(syscall)
        self.calc_syscall_type_distribution()
        ids_info = {
            'score': self.ids.consume_system_call(syscall), 
            'state': self.ids._model_state.value,
            'training_size': self.ids._training_size,
            'current_ngrams': self.ids._normal_ngrams["training_size"]
        }
        self.handle_ids_info(ids_info)

    def calc_syscall_type_distribution(self):
        """
        scan through deque and read syscall type dictionary
        sum occurences of each syscall and save summed dictionary 
        """
        #iterate through all syscall_type_dicts in deque
        # if MAX_BUCKETS=1 only one entry in deqeue_syscall_type_per_second
        for syscall_type_dict in self.deque_syscall_type_per_second:
            # iterate through different types of syscalls in dict
            for syscall_type in syscall_type_dict:
                #sum up all entries, if not existent -> add entry
                if syscall_type in self.syscall_type_dict:
                    self.syscall_type_dict[syscall_type] += syscall_type_dict[syscall_type]
                else:
                    self.syscall_type_dict[syscall_type] = syscall_type_dict[syscall_type]
        if(self.deque_syscall_type_per_second):
            self.syscall_type_dict_last_second = self.deque_syscall_type_per_second.pop()
        

    def get_syscall_type_distribution_second(self):
        """
        return syscall_type distribution for last second if existent 
        (could be ask before syscall information received -> return None)
        :return syscall_type_dict_last_second
        """
        if not (self.syscall_type_dict_last_second == None):
            tmp = self.syscall_type_dict_last_second
            self.syscall_type_dict_last_second = None
            return tmp
        return None 
                
    def get_syscall_type_distribution(self):
        """
        sort syscall type frequency 
        embed sorted list in dictionary 
        :return sorted syscall_type_distribution
        """
        #sort dictionary 
        list_of_dicts = [] 
        sorted_tuples = sorted(self.syscall_type_dict.items(), reverse=True, key=lambda x: x[1])
        for elem in sorted_tuples:
            tmp_dict = {}
            tmp_dict[elem[0]] = elem[1]
            list_of_dicts.append(tmp_dict)
        #sorted_dict = {key: value for key, value in sorted(self.syscall_type_dict.items(), reverse=True, key=lambda item: item[1])}
        sorted_dict = {
            "sorted_syscalls": list_of_dicts
        } 
        return sorted_dict 

    def handle_ids_info(self, ids_info):
        """
        Add ids scores to save until next statistic update
        """
        if not ids_info['score'] == None:
            self.ids_info['score_list'].append(ids_info['score'])
        self.ids_info = {
            'score': ids_info['score'],
            'score_list': self.ids_info['score_list'],
            'state': ids_info['state'],
            'training_size': ids_info['training_size'],
            'current_ngrams': ids_info['current_ngrams'] 
        } 

    def get_ids_score(self):
        # if list is not empty return highest score
        if self.ids_info['score_list']:
            # sort list and return highest score
            sorted_ids_scores = sorted(self.ids_info['score_list'], reverse=True)
            self.ids_info['score_list']= list()
            highest_score = sorted_ids_scores[0]
            return highest_score
        return 0 


    def calc_sum(self):
        self.syscall_sum += 1
        return None

    def get_sum(self):
        return self.syscall_sum

    def calc_calls_per_bucket(self, syscall):
        rawtime_of_syscall = syscall[1]
        syscall_type = syscall[6]
        if self.start_time == 0:
            self.start_time = int(rawtime_of_syscall)

        # count all syscall occurences per bucket_update_delay
        # additionaly count different types of calls
        if int(rawtime_of_syscall) - self.start_time < self.bucket_update_delay:
            if self.bucket_counter == 0:
                start_timestamp = int(rawtime_of_syscall)
            self.bucket_counter += 1
            # TODO ADD SYSCALL TYPE CORRECT NOT ONE PER BUCKET
            # add entry to dictionary, count type of systemcall to bucket information
            if syscall_type in self.syscall_type_dict_bucket:
                self.syscall_type_dict_bucket[syscall_type] += 1
            else:
                self.syscall_type_dict_bucket[syscall_type] = 1


        # add newest bucket to deque and pop oldest if more than MAX_BUCKETS entries
        else:
            deque_entry = [self.bucket_counter, self.start_time]
            self.deque_syscall_per_second.append(deque_entry)
            self.deque_syscall_type_per_second.append(self.syscall_type_dict_bucket)
            if len(self.deque_syscall_per_second) > MAX_BUCKETS:
                dropped = self.deque_syscall_per_second.popleft()
            self.bucket_counter = 0
            self.syscall_type_dict_bucket = {}
            self.start_time = int(rawtime_of_syscall)

    def get_calls_per_second(self):
        # current_time = int(round(time.time() * 1000))
        # last_bucket_time = current_time
        syscall_counter = 0
        for syscall in self.deque_syscall_per_second:
            syscall_counter += syscall[0]
        if (self.deque_syscall_per_second):
            self.deque_syscall_per_second.popleft()
        return syscall_counter
