from collections import deque
from enum import Enum, IntEnum

import numpy
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import initializers
from tensorflow.keras.constraints import max_norm

#from algorithms.TimedStopping import TimedStopping
#from helper.Constants import DataStream
#from helper.Constants import FastStreamIndex
#from helper.Constants import ModelState
from syscalls_to_vec_mlp import Mode

#TODO Auslagern
class ModelState(Enum):
    """
    this enum class gives constants for model states
    """
    # the model is in training state
    Training = 0
    # the model is in detection state
    Detection = 1

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


class MLP:


    def __init__(self, syscall_map, ngram_length=7, window_length=1000, thread_aware=True):
        """
        create the MLP classifier (Multi Layer Perceptron)
        gets n-grams of system calls as input
        example:
        n = 4
        n-gram x = [x_0,x_1,x_2,x_3]
        uses the first part [x_0,x_1,x_2] as input to the network
        uses the second part [x_3] as expected Label as output of the network

        :param ngram_length: the ngram length to use - so minimum n = 2
        :param window_length: the sliding window size
        """
        self._ngram_length = ngram_length
        self._window_length = window_length

        # dict for all syscall buffers:        
        self._system_call_buffer = {}
        self._syscall_to_int = {}
        self._int_to_syscall = {}

        # Keras Model object
        self.mlp = None

        # training matrix size
        self.number_of_cols = 0
        self.number_of_rows = 0

        # the normal db
        self._normal_ngrams = {}

        # save already calculated results in this dict to avoid recalculating them
        # ngram -> result (dont save the ohes)
        self._result_dict = {}

        # reusable buffer for one ohe
        self._row_buffer = None

        # model state
        self._model_state = ModelState.Training

        # dict for mismatches, uses a deque of fixed length to calculate moving average mismatch values
        # self._mismatch_buffers = deque(maxlen=self._window_length)
        self._mismatch_buffer = {}
        self._moving_sum_value = 0

        self._thread_aware = thread_aware

        self.syscall_map = syscall_map
        self._num_syscalls = 0
        self._num_threads_seen = 0
        self._num_files_seen = 0
        self._mode = syscall_map._mode

        self._last_seen_ngram = None

    def consume_system_call(self, syscall):
        """
        this method takes system calls and builds ngrams with them
        the system calls may be encoded as integers ( must be converted to one hot encoding (ohe)) or tuple of floats (w2v)
        then it passes these ngrams to _train_on or _detect
        and returns their result value
        :param syscall: the system call to work on
        :return: the anomaly score (value >= 0) or either DataStream.EndOfFile or DataStream.AttackStarts
        """
        result = 0
        # get the system call number or tuple (if system_calls_as_vector == True)
        syscall_number = self._get_syscall_as_int(syscall[Index.SystemCall])

        # special cases:
        # - End Of File: (DataStream.EndOfFile, None, None)
        # - Attack Starts: (DataStream.AttackStarts, relative_time_stamp, None) (start of the attack to the second)
        #if syscall_number == DataStream.EndOfFile:
            #self._eof()
            #return DataStream.EndOfFile

        #if syscall_number == DataStream.AttackStarts:
            #return DataStream.AttackStarts

        # get the thread id and check/prepare buffers

        #TODO Event direction
        #if syscall[Index.EventDirection] == ">":
        thread_id = 0
        if self._thread_aware:
            thread_id = syscall[Index.ThreadID]

        if thread_id not in self._system_call_buffer:
            self._system_call_buffer[thread_id] = deque(maxlen=self._ngram_length)

        # add the current system call to the buffer
        self._system_call_buffer[thread_id].append(syscall_number)

        # Do we have a new n-gram?
        ngram_tuple = None
        if len(self._system_call_buffer[thread_id]) == self._ngram_length:
            ngram_tuple = tuple(self._system_call_buffer[thread_id])
            self._last_seen_ngram = ngram_tuple
        if ngram_tuple is not None:
            # are we in training modefor this container?
            if self._model_state == ModelState.Training:
                # do the training thing
                self._train_on(ngram_tuple)
            # are we in detection mode?
            elif self._model_state == ModelState.Detection:
                # do the detection thing
                result = self._detect(ngram_tuple)
        return result

    def _build_mlp_model(self, number_of_cols):        
        self._hidden_layer_size = 100
        self._num_layers = 2
        self._dropout = 0.5
        self._max_norm_value = 2.0
        self._loss = keras.losses.MeanSquaredError()
        self._optimizer=keras.optimizers.Adam()
        self._activation_function = "selu"

        # input
        input_layer = keras.Input(shape=(number_of_cols,), dtype="float32", name="input_layer")
        x = input_layer

        for i in range(self._num_layers):
            x = keras.layers.Dense(
                self._hidden_layer_size,
                activation="relu",
                name="hidden_{}".format(i),
            )(x)
            x = keras.layers.Dropout(self._dropout)(x)
        # output
        output_layer = keras.layers.Dense(
            self._num_syscalls + 1, # to include the +1 class (unknown)
            activation="softmax",
            name="output_layer",
        )(x)
        self.mlp = keras.Model(inputs=input_layer, outputs=output_layer, name="simple_mlp")
        self.mlp.summary()
        self.mlp.compile(loss=self._loss, optimizer=self._optimizer)

    def switch_to_detection(self):
        """
        This method is called once after all training data was seen by consume_system_call.
        It will build the autoencoder, the training matrix and will call fit on the model.
        Finally it will switch the model_state to ModelState.Detection.
        """
        distinct_ngrams = len(self._normal_ngrams)
        # set the _num_syscalls to the number of syscalls seen in training + 1 (this is needed later for the unknown syscalls)
        self._num_syscalls = len(self.syscall_map._seen_syscalls) + 1
        #threads_per_file = self._num_threads_seen/self._num_files_seen

        #print("  saw on avg. {} different threads".format(threads_per_file))
        print("  saw overall {} different ngrams".format(distinct_ngrams))
        print("  saw overall {} different system calls".format(self._num_syscalls))

        # prepare the training matrix        
        if self._mode == Mode.W2V or self._mode == Mode.W2V_SCENARIO:
            # -1, since the last system call is the expected output and therefore does not belong to the input
            self.number_of_cols = self.syscall_map._vector_size * (self._ngram_length - 1)
        if self._mode == Mode.INT:
            # same as above
            self.number_of_cols = self._num_syscalls * (self._ngram_length - 1)
        self.number_of_rows = distinct_ngrams
        training_matrix = numpy.zeros((self.number_of_rows, self.number_of_cols), dtype="single")
        label_matrix = numpy.zeros((self.number_of_rows, self._num_syscalls + 1), dtype="single")
        # build the model:
        self._build_mlp_model(self.number_of_cols)

        # prepare the row buffer for use in detection mode
        self._row_buffer = numpy.zeros((1, self.number_of_cols), dtype="single")

        # calculate all OHEs and build the training matrix
        if self._mode == Mode.INT:
            row = 0
            for ngram in self._normal_ngrams:
                # each ngram consists of n integer (starting with 1) representing a system call
                # the first n-1 system calls are used as input to the training
                i = 0
                for syscall in ngram[:-1]:
                    #import pdb; pdb.set_trace()
                    #print(syscall)
                    # calculate the one hot encoding for the training syscalls                
                    training_matrix[row][i * self._num_syscalls + syscall - 1] = 1
                    i += 1
                # the last system call is used as expected result for the training
                # to use the softmax function we have to represent this last system
                # call as one hot encoded vector
                label_matrix[row][ngram[-1]-1] = 1
                row += 1
        if self._mode == Mode.W2V or self._mode == Mode.W2V_SCENARIO:
            row = 0
            for ngram in self._normal_ngrams:
                # each ngram consists of n vectors of a given length representing a system call
                # the first n-1 system calls (vectors) are used as input to the training
                i = 0
                for syscall in ngram[:-1]:
                    for v in syscall:
                        training_matrix[row][i] = v
                        i += 1
                # the last system call is used as expected result for the training
                # to use the softmax function we have to represent this last system
                # call as one hot encoded vector
                label_matrix[row][self.syscall_map.get_ohe_index_from_vector(ngram[-1]) - 1] = 1
                row += 1
        # finally fit the mlp
        print(f"matrix.shape = {training_matrix.shape} --> {training_matrix.size}")
        callback_early_stopping = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
        #callback_timed_stopping = TimedStopping(seconds=5*60*60,verbose=1) # stop after 5h = 5 * 60 * 60 seconds
        self.mlp.fit(training_matrix, label_matrix, batch_size=128, epochs=1000, validation_split=0.0, callbacks=[callback_early_stopping], verbose=2)

        # initialize the mismatch buffer here
        self._mismatch_buffer = deque(iterable=[0] * self._window_length, maxlen=self._window_length)
        self._moving_sum_value = 0

        print("switching to detection mode")
        # set state to detection
        self._model_state = ModelState.Detection

        return distinct_ngrams, self._num_syscalls

    def _eof(self):
        self._num_files_seen += 1
        self._num_threads_seen += len(self._system_call_buffer)
        self._system_call_buffer.clear()
        self._mismatch_buffer = deque(iterable=[0] * self._window_length, maxlen=self._window_length)
        self._moving_sum_value = 1

    def _train_on(self, ngram_tuple):
        """
        Is the given ngram already known to us?
        If yes: do nothing!
        If no: remember this ngram!
        :param ngram_tuple: the ngram to train
        :return: -
        """
        if ngram_tuple not in self._normal_ngrams:
           self._normal_ngrams[ngram_tuple] = 1

    def _detect(self, ngram_tuple):
        """
        checks the given ngram against result db or calculates the score for the ngram
        :param ngram_tuple:
        :return: the moving average mismatch value (float)
        """
        # first get the most left value from the window of this container
        left_value = self._mismatch_buffer.popleft()

        # Is the result for this tuple already known?
        right_value = self._result_dict.get(ngram_tuple, None)
        if right_value is None:

            if self._mode == Mode.W2V or self._mode == Mode.W2V_SCENARIO:
                # Remember: we have a tuple of tuples here!
                # Know build a singe numpy array from it.
                i = 0
                for syscall in ngram_tuple[:-1]:
                    for v in syscall:
                        self._row_buffer[0][i] = v
                        i += 1

                # determine the expected index
                expected_index = self.syscall_map.get_ohe_index_from_vector(ngram_tuple[-1]) - 1
                if expected_index > self._num_syscalls:
                    expected_index = self._num_syscalls

                # predict for the given data
                result_vector = self.mlp(self._row_buffer, training=False)

                # get the probability of the actual syscall
                right_value = 1.0 - result_vector[0][expected_index].numpy()
                self._result_dict[ngram_tuple] = right_value

                #print("------------")
                #print(ngram_tuple)
                #print("expected = {}".format(expected_index))
                #print(result_vector)
                #print(right_value)


            if self._mode == Mode.INT:
                # calculate the ohe and ask the model for help ;)
                i = 0
                for syscall in ngram_tuple[:-1]:
                    # if we have some new syscalls in the data we had not seen in training - we set them to _num_syscalls (which is actually the real number of syscalls in training + 1)
                    if syscall > self._num_syscalls:
                        syscall = self._num_syscalls
                    self._row_buffer[0][i * self._num_syscalls + syscall - 1] = 1
                    i += 1

                # determine the expected index (easy since we get the index directly)
                expected_index = ngram_tuple[-1] - 1
                if expected_index > self._num_syscalls:
                    expected_index = self._num_syscalls

                # predict for the given data
                result_vector = self.mlp(self._row_buffer, training=False)

                # get the probability of the actual syscall
                right_value = 1.0 - result_vector[0][expected_index].numpy()
                self._result_dict[ngram_tuple] = right_value

                i = 0
                for syscall in ngram_tuple[:-1]:
                    # if we have some new syscalls in the data we had not seen in training - we set them to _num_syscalls (which is actually the real number of syscalls in training + 1)
                    if syscall > self._num_syscalls:
                        syscall = self._num_syscalls                                
                    self._row_buffer[0][i * self._num_syscalls + syscall - 1] = 0
                    i += 1                

        # add the value to the mismatch buffer
        self._mismatch_buffer.append(right_value)

        # calculate the moving average mismatch value and return it
        # "when calculating successive values, a new value comes into the sum, and the oldest value drops out,
        #  meaning that a full summation each time is unnecessary for this simple case."
        self._moving_sum_value = self._moving_sum_value - left_value + right_value
        return self._moving_sum_value / self._window_length

    def get_desc(self):
        desc = "hidden_layer_size={} dropout={} max_norm_value={} num_layers={} lossfunction={} activationfunction={} optimizer={}".format(            
            self._hidden_layer_size,
            self._dropout, 
            self._max_norm_value, 
            self._num_layers, 
            type(self._loss).__name__, 
            self._activation_function, 
            type(self._optimizer).__name__)
        return desc

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
