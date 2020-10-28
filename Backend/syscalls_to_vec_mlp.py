import pathlib
from enum import Enum

class Mode(Enum):
    INT = 1
    W2V = 2    
    STR = 3
    W2V_SCENARIO = 4

class SyscallsToVec:
    """
    This class holds mappings from system call strings to feature vectors and back.
    It supports three modes:
    Mode.INT - Each system call is mapped to an integer.
    Mode.W2V - Each system call is mapped to a vector of fixed length, calculated by word 2 vec on the lidds corpus.
    Mode.W2V_SCENARIO - Each system call is mapped to a vector of fixed length, calculated by word 2 vec on the training data of a scenario specific corpus.
    Mode.STR - Each system call is mapped to its name as string
    """

    def __init__(self, mode=Mode.INT, vector_size=None, scenario=None, use_adfa=False):

        self._forward_map = {}
        self._reverse_map = {}
        self._seen_syscalls = {}
        self._mode = mode
        self._vector_size = vector_size

        ### Mode.W2V ###
        if self._mode == Mode.W2V:
            # there are only vectors available for 2, 3 and 10
            if vector_size not in [2, 3, 10]:
                print("There are only W2V vectors available for 2, 3 and 10! Set vector_size to 2.")
                vector_size = 2
            if use_adfa == True:
                print("using adfa-ld embeddings")
                self._syscall_vector_file = pathlib.Path("syscalls/word2vec_embeddings", "adfa-ld_{}.w2v".format(self._vector_size))                
            else:
                print("using lid-ds embeddings")
                self._syscall_vector_file = pathlib.Path("syscalls/word2vec_embeddings", "lidds_vectors_{}.txt".format(self._vector_size))
                
            
            self._unknown_vector = tuple([100] * self._vector_size)

            with open(self._syscall_vector_file) as file:
                next(file)  # skip the header line
                for line in file:
                    line = line[:-2]  # remove the tailing space and newline: " \n"
                    # split the line at all spaces
                    tmp_list = line.split(" ")
                    # extract the system call from position 0
                    system_call = tmp_list[0]
                    # the rest is the vector, use tuple as data type, it may be used as key in dicts
                    vector = tuple(tmp_list[1:])
                    
                    self._forward_map[system_call] = vector
                    self._reverse_map[vector] = system_call

        ### Mode.W2V_SCENARIO ###
        if self._mode == Mode.W2V_SCENARIO:
            # there are only vectors available for 2,3,4,5 and 10
            if vector_size not in [2, 3, 4, 5, 10]:
                print("There are only scenario specific W2V vectors available for 2, 3, 4, 5 and 10! Set vector_size to 2.")
                vector_size = 2
            print("using lid-ds scenario wise embeddings")
            self._syscall_vector_file = pathlib.Path("syscalls/word2vec_embeddings", "{}_{}.w2v".format(scenario, self._vector_size))
            self._unknown_vector = tuple([100] * self._vector_size)

            with open(self._syscall_vector_file) as file:
                next(file)  # skip the header line
                for line in file:
                    line = line[:-2]  # remove the tailing space and newline: " \n"
                    # split the line at all spaces
                    tmp_list = line.split(" ")
                    # extract the system call from position 0
                    system_call = tmp_list[0]
                    # the rest is the vector, use tuple as data type, it may be used as key in dicts
                    vector = tuple(tmp_list[1:])
                    
                    self._forward_map[system_call] = vector
                    self._reverse_map[vector] = system_call

    def get_feature_vector_from_system_call(self, syscall_string):
        """
        returns the vector of the given system call

        :param syscall: the system call as string e.g.: "open"
         
                if mode == Mode.W2V: the corresponding vector
of this system call or a zero-vector 
                                     if the given system call is not known
                if mode == Mode.INT: the corresponding int representing this system call 
                if mode == Mode.STR: the name is returned as string
                else: None
        """
        # to keep track of seen system calls
        if syscall_string not in self._seen_syscalls:
            number = len(self._seen_syscalls) + 1
            self._seen_syscalls[syscall_string] = number

        if self._mode == Mode.W2V:
            return self._forward_map.get(syscall_string, self._unknown_vector)
        elif self._mode == Mode.W2V_SCENARIO:
            return self._forward_map.get(syscall_string, self._unknown_vector)
        elif self._mode == Mode.INT:
            if syscall_string not in self._forward_map:
                # insert this syscall if not known
                syscall_number = len(self._forward_map) + 1
                self._forward_map[syscall_string] = syscall_number
                self._reverse_map[syscall_number] = syscall_string
            else:
                syscall_number = self._forward_map.get(syscall_string)
            return syscall_number
        elif self._mode == Mode.STR:
            return syscall_string
        else:
            return None

    def get_systemcall_name_from_vector(self, feature_vector):
        """
        returns the system call for the given feature_vector or "UNKNOWN" if it is unknown
        :param feature_vector: the feature_vector as tuple if mode == Mode.W2V or as int it mode == Mode.INT
        :return: the system call e.g. "close" or "UNKNOWN"
        """
        return self._reverse_map.get(feature_vector, "UNKNOWN")

    def get_ohe_index_from_vector(self, feature_vector):
        syscall_name = self.get_systemcall_name_from_vector(feature_vector)
        return self._seen_syscalls.get(syscall_name, len(self._seen_syscalls) + 1)

