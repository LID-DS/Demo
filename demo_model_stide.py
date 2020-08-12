from collections import deque
from enum import Enum
from enum import IntEnum
import pickle

from analyse_alarm import Analysis



class Index(IntEnum):
    """
    this enum class gives the indices of each field in the data
    """
    # event direction
    EventDirection = 5
    # the thread id
    ThreadID = 4
    # the actual system call
    SystemCall = 6


class ModelState(Enum):
    """
    this enum class gives constants for model states
    """
    # the model is in training state
    Training = 0
    # the model is in detection state
    Detection = 1


class DemoModelStide:
    def __init__(
            self,
            ngram_length=7,
            window_length=1000,
            training_size=10000000,
            trained_model=None):
        """
        create the STIDE classifier
        :param ngram_length: the ngram length to use
        :param window_length: the sliding window size
        :param training_size: the number of system calls
            seen before switching into detection mode
        """
        ###
        self._alarm_threshold = 0.05
        self._consecutive_alarm = False
        ###
        self._ngram_length = ngram_length
        self._window_length = window_length

        # dict for all syscall buffers:
        # self._system_call_buffers[thread_id] = deque(ngram_size)
        self._system_call_buffer = {}

        if trained_model is None:
            self._training_size = training_size
            # dict for all normal ngrams (the "normal" database)
            # self._normal_ngrams[ngram_tuple] = count
            self._normal_ngrams = {}
            self._normal_ngrams["training_size"] = 0
            # dict for model states
            # self._model_states = ModelStatus.Training
            self._model_state = ModelState.Training
            # dict for mismatches, uses a deque of fixed length to calculate
            # moving average mismatch values
            # self._mismatch_buffers = deque(maxlen=self._window_length)
            self._mismatch_buffer = {}
            self._moving_sum_value = 0
            # dict to convert system calls from string to int ( "close" -> 1)
            self._syscall_to_int = {}
            # dict to convert system calls from int to string ( 1 -> "close")
            self._int_to_syscall = {}

        else:
            self._training_size = trained_model._normal_ngrams['training_size']
            self._normal_ngrams = trained_model._normal_ngrams
            self._model_state = ModelState.Detection
            # initialize the mismatch buffer here
            self._mismatch_buffer = deque(iterable=[0] * self._window_length,
                                          maxlen=self._window_length)
            self._moving_sum_value = 0

            # dict to convert system calls from string to int ( "close" -> 1)
            self._syscall_to_int = trained_model._syscall_to_int
            # dict to convert system calls from int to string ( 1 -> "close")
            self._int_to_syscall = trained_model._int_to_syscall
        ###
        self.analysis = Analysis(self._window_length)
        ###

    def _get_syscall_as_int(self, syscall_string):
        """
        from a given system call string -> return a corresponding number
        :param syscall_string: the system call string to convert
        :return: an integer representing the given system call
            regarding this model instance
        """
        # extract the system call
        if syscall_string not in self._syscall_to_int:
            # insert this syscall if not known
            syscall_number = len(self._syscall_to_int) + 1
            self._syscall_to_int[syscall_string] = syscall_number
            self._int_to_syscall[syscall_number] = syscall_string
        else:
            syscall_number = self._syscall_to_int.get(syscall_string)
        return syscall_number

    def _train_on(self, ngram_tuple):
        """
        adds the given ngram_tuple to the normal database
        if the number of system call seen  is bigger than self._training_size
        it will switch to detection mode
        :param ngram_tuple: the ngram to train
        :return: -
        """
        # add the ngram tuple
        if ngram_tuple in self._normal_ngrams:
            self._normal_ngrams[ngram_tuple] += 1
        else:
            self._normal_ngrams[ngram_tuple] = 1

        self._normal_ngrams["training_size"] += 1
        if self._normal_ngrams["training_size"] >= self._training_size:
            print("switching to detection mode")
            distinct_ngrams = len(self._normal_ngrams)
            print("  saw {} different ngrams".format(distinct_ngrams))
            self._model_state = ModelState.Detection
            # initialize the mismatch buffer here
            self._mismatch_buffer = deque(
                iterable=[0] * self._window_length,
                maxlen=self._window_length)
            self._moving_sum_value = 0

    def _detect(self, ngram_tuple):
        """
        checks the given tuple against the normal db and calculates
        the anomaly score
        :param ngram_tuple:
        :return: the moving average mismatch value (float)
        """

        # first get the most left value from the window of this container
        left_value = self._mismatch_buffer.popleft()

        # is the tuple a mismatch?
        # 0 for no, 1 for yes
        right_value = \
            1 if (self._normal_ngrams.get(ngram_tuple) is None) else 0

        # add the count to the mismatch buffer
        self._mismatch_buffer.append(right_value)

        # calculate the moving average mismatch value and return it
        # when calculating successive values,
        # a new value comes into the sum, and the oldest value drops out,
        # meaning that a full summation each time is unnecessary
        # for this simple case.
        self._moving_sum_value = \
            self._moving_sum_value - left_value + right_value
        ###
        mv_sum = self._moving_sum_value / self._window_length
        if mv_sum < self._alarm_threshold:
            self.analysis.track_mv_window(ngram_tuple)
        if mv_sum >= self._alarm_threshold:
            self.analysis.alarm = True 
            if not self._consecutive_alarm:
                self.analysis.save_current_window(
                        ngram_tuple=ngram_tuple,
                        score=mv_sum,
                        mismatch_value=right_value,
                        consecutive_alarm=self._consecutive_alarm)
                self._consecutive_alarm = True
            else:
                self.analysis.save_current_window(
                        ngram_tuple=ngram_tuple,
                        score=mv_sum,
                        mismatch_value=right_value,
                        consecutive_alarm=self._consecutive_alarm)
        elif self._consecutive_alarm:
            self.analysis.alarm = False
            self.analysis.save_current_window(
                    ngram_tuple=None,
                    score=None,
                    mismatch_value=None,
                    consecutive_alarm=False)
            self._consecutive_alarm = False
        ###
        return self._moving_sum_value / self._window_length

    def consume_system_call(self, syscall):
        """
        this method takes system calls and classifies them
        :param syscall: the system call to classify
        :return: the anomaly score
        """
        result = None
        # event direction:
        # > for enter events
        # < for exit events
        # for stide we just use the opening system call events ">"
        ###
        if self.analysis.alarm:
            self.analysis.save_raw_syscall(syscall, self._get_syscall_as_int(syscall[Index.SystemCall]))
        ###
        if syscall[Index.EventDirection] == ">":
            # get the system call number
            syscall_number = \
                    self._get_syscall_as_int(syscall[Index.SystemCall])

            # get the thread id and check/prepare buffers
            thread_id = syscall[Index.ThreadID]
            if thread_id not in self._system_call_buffer:
                self._system_call_buffer[thread_id] = \
                        deque(maxlen=self._ngram_length)

            # add the current system call to the buffer
            self._system_call_buffer[thread_id].append(syscall_number)

            # Do we have a new n-gram?
            ngram_tuple = None
            if len(self._system_call_buffer[thread_id]) == self._ngram_length:
                ngram_tuple = tuple(self._system_call_buffer[thread_id])
            if ngram_tuple is not None:
                # are we in training mode for this container?
                if self._model_state == ModelState.Training:
                    # do the training thing
                    self._train_on(ngram_tuple)
                # are we in detection mode?
                elif self._model_state == ModelState.Detection:
                    # do the detection thing
                    result = self._detect(ngram_tuple)
        return result

    def pipe_alarm_files(self):
        """
        analysis only accessible from IDS
        return filenames so it can be accessed in backend 
        and sent to frontend
        """
        return self.analysis.alarm_filenames

    def _ngram_tuple_to_str(self, ngram_tuple):
        """
        converts a tuple of ints to a readable string eg:
            (1,4,2) -> "open read close"
        :param ngram_tuple: the tuple of ngrams to convert
        :return: a readable string of this tuple
        """
        string = ""
        for syscall_int in ngram_tuple:
            string += self._int_to_syscall[syscall_int] + " "
        return string[:-1]

    def _load_model(self):
        """
        load saved _normal_ngrams
        """
        with open('Models/save_ngrams.p', 'rb') as ngrams_location:
            self._normal_ngrams = pickle.load(ngrams_location)
        with open('Models/save_sys_to_int.p', 'rb') as sys_int_location:
            self._syscall_to_int = pickle.load(sys_int_location)
        with open('Models/save_int_to_sys.p', 'rb') as int_sys_location:
            self._int_to_syscall = pickle.load(int_sys_location)
        return self

    def _save_model(self):
        """
        save model:
            _normal_ngrams to store trained ngrams (syscall as integer)
            syscall_to_int and
            int_to_syscall to convert integers to syscall strings and back.
        """
        with open('Models/save_ngrams.p', 'wb') as ngram_location:
            pickle.dump(self._normal_ngrams, ngram_location)
        with open('Models/save_sys_to_int.p', 'wb') as sys_int_location:
            pickle.dump(self._syscall_to_int, sys_int_location)
        with open('Models/save_int_to_sys.p', 'wb') as int_sys_location:
            pickle.dump(self._int_to_syscall, int_sys_location)
