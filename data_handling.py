import collections
import operator
from demo_model_stide import DemoModelStide

MAX_BUCKETS = 1
INITIAL_TRAINING_SIZE = 10000000
MAX_TOP_NGRAMS = 10
ALARM_THRESHOLD = 0.05


class DataHandling:

    def __init__(self):
        """
        Initialization of DataHandling
            In charge of:
                calculation of statistics of systemcalls
                    sum
                    calls per bucket (set to second -> bucket delay
                    syscall distribution
                collection of ids information (score, state...)
        """
        self.ids = DemoModelStide(training_size=INITIAL_TRAINING_SIZE)
        self.syscall_sum = 0
        self.start_time = 0
        self.bucket_counter = 0
        self.bucket_update_delay = 1000
        self.deque_syscall_per_second = collections.deque()
        self.deque_syscall_type_per_second = collections.deque()
        self.syscall_type_dict_bucket = {}
        self.syscall_type_dict = {}
        self.syscall_type_dict_last_second = {}
        self.ids_info = {
            'score': 0,
            'score_list': [],
            'state': self.ids._model_state.value,
            'training_size': self.ids._training_size,
            'current_ngrams': 0,
        }

    def update_statistic(self, syscall):
        """
        received syscall from syscallhandling
        calc new:
            sum of syscalls
            syscalls in last <bucket_size> (e.g 1 second)
            syscall distribution
            send syscall to IDS to gather ids information
                score
                state
                training size
                current seen ngrams
        first calc_syscall_type_distribution than calls_per_bucket
            -> calls_per_bucket removes bucket if scanned
        """
        self.calc_sum()
        self.calc_syscall_type_distribution()
        self.calc_calls_per_bucket(syscall)
        # hand over system call to IDS
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
        # iterate through all syscall_type_dicts in deque
        # if MAX_BUCKETS=1 only one entry in deqeue_syscall_type_per_second
        for syscall_type_dict in self.deque_syscall_type_per_second:
            # iterate through different types of syscalls in dict
            for syscall_type in syscall_type_dict:
                # sum up all entries, if not existent -> add entry
                if syscall_type in self.syscall_type_dict:
                    self.syscall_type_dict[syscall_type] += (
                        syscall_type_dict[syscall_type]
                    )
                else:
                    self.syscall_type_dict[syscall_type] = (
                        syscall_type_dict[syscall_type]
                    )
        if(self.deque_syscall_type_per_second):
            self.syscall_type_dict_last_second = (
                self.deque_syscall_type_per_second.pop()
            )

    def handle_ids_info(self, ids_info):
        """
        Add ids scores to save until next statistic update
        than score list is reset
        """
        if not ids_info['score'] is None:
            self.ids_info['score_list'].append(ids_info['score'])
        self.ids_info = {
            'score': ids_info['score'],
            'score_list': self.ids_info['score_list'],
            'state': ids_info['state'],
            'training_size': ids_info['training_size'],
            'current_ngrams': ids_info['current_ngrams']
        }

    def get_syscall_type_distribution_second(self):
        """
        return syscall_type distribution for last second if existent
        (could be ask before syscall information received -> return None)
        :return syscall_type_dict_last_second
        """
        if not (self.syscall_type_dict_last_second is None):
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
        # sort dictionary
        list_of_dicts = []
        sorted_tuples = sorted(
                self.syscall_type_dict.items(),
                reverse=True,
                key=lambda x: x[1])

        for elem in sorted_tuples:
            tmp_dict = {}
            tmp_dict[elem[0]] = elem[1]
            list_of_dicts.append(tmp_dict)
        # embed to dictionary (easier to send via websocket)
        sorted_dict = {
            "sorted_syscalls": list_of_dicts
        }
        return sorted_dict

    def get_ids_score(self):
        """
        get highest ids score of current list of scores
        than reset score list
        if list empty return 0
        """
        # if list is not empty return highest score
        if self.ids_info['score_list']:
            # sort list and return highest score
            sorted_ids_scores = sorted(
                    self.ids_info['score_list'],
                    reverse=True)
            self.ids_info['score_list'] = list()
            highest_score = sorted_ids_scores[0]
            return highest_score
        return 0

    def get_sum(self):
        return self.syscall_sum

    def get_calls_per_second(self):
        """
        gets called every second
        count systemcalls in buckets
        pop oldest bucket
        """
        syscall_counter = 0
        for syscall_bucket in self.deque_syscall_per_second:
            syscall_counter += syscall_bucket[0]
        if self.deque_syscall_per_second:
            self.deque_syscall_per_second.popleft()
        return syscall_counter

    def get_top_ngrams(self):
        """
        return MAX_TOP_NGRAMS most seen ngrams
        """
        # get current normal ngrams of ids
        ngram_dict = self.ids._normal_ngrams

        # TODO why next line not working?
        # TODO converting list to dict and than dict to list, really?
        # del ngram_dict['training_size']

        # sort dict so highest is in first position
        top_ngrams = dict(
            sorted(
                ngram_dict.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:MAX_TOP_NGRAMS + 1]
        )
        # remove first entry which stores only training_size
        del top_ngrams['training_size']

        if len(self.ids._normal_ngrams) > MAX_TOP_NGRAMS + 1:
            rest_ngrams = sorted(
                    ngram_dict.items(),
                    key=operator.itemgetter(1),
                    reverse=True
                )[MAX_TOP_NGRAMS + 1:]
            sum_of_other_ngrams = 0
            for i in range(len(rest_ngrams)):
                sum_of_other_ngrams += rest_ngrams[i][1]
        top_list = []
        for key, value in top_ngrams.items():
            temp = [key, value]
            top_list.append(temp)
        if len(self.ids._normal_ngrams) > MAX_TOP_NGRAMS + 1:
            top_list.append(['others', sum_of_other_ngrams])

        return top_list

    def get_int_to_sys(self):
        """
        create list of conversion of integer used in ids
        and the actual syscall string
        """
        int_to_syscall_list = []
        for key, value in self.ids._int_to_syscall.items():
            temp = [key, value]
            int_to_syscall_list.append(temp)
        return int_to_syscall_list

    def calc_sum(self):
        self.syscall_sum += 1
        return None

    def calc_calls_per_bucket(self, syscall):
        """
        in intervall of bucket_update_delay sum syscall ocurrences
        if intervall is over add bucket to dequeue.
            (with sum and syscall type distribution)
        if more than MAX_BUCKETS in dequeue pop oldest entry
        """
        rawtime_of_syscall = syscall[1]
        syscall_type = syscall[6]
        if self.start_time == 0:
            self.start_time = int(rawtime_of_syscall)

        # count all syscall occurences per bucket_update_delay
        # additionaly count different types of calls
        if int(rawtime_of_syscall) - self.start_time < self.bucket_update_delay:
            self.bucket_counter += 1
            # add entry to dictionary,
            # count type of systemcall to bucket information
            if syscall_type in self.syscall_type_dict_bucket:
                self.syscall_type_dict_bucket[syscall_type] += 1
            else:
                self.syscall_type_dict_bucket[syscall_type] = 1

        # add newest bucket to deque and
        # pop oldest if more than MAX_BUCKETS entries
        else:
            deque_entry = [self.bucket_counter, self.start_time]
            self.deque_syscall_per_second.append(deque_entry)
            self.deque_syscall_type_per_second.append(
                    self.syscall_type_dict_bucket)
            if len(self.deque_syscall_per_second) > MAX_BUCKETS:
                self.deque_syscall_per_second.popleft()
            self.bucket_counter = 0
            self.syscall_type_dict_bucket = {}
            self.start_time = int(rawtime_of_syscall)
