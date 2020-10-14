from datetime import date
from shutil import copyfile
import os
import time
import collections
import data_handling

class Analysis:
    """
    keep track of current window of syscall and handle syscall which
    triggered an alarm
    """

    def __init__(self, window_length):
        """
        Initialize window_length and deque which keeps track of window
        :params: window_length of moving window of system calls
        """
        self.window_length = window_length
        self.deque_window = collections.deque()
        self.consecutive_alarm_list = []
        self.alarm = False
        self.alarm_count = 0
        self.last_alarm_content = ""
        self.last_alarm_queue = collections.deque()

    def save_raw_syscall(self, syscall, syscall_num):
        """
        extract needed information of raw system call for later analysis
        :params: syscall raw system call information
        :params: syscall_num ids converts syscall names to int
        """
        rawtime = str(syscall[1])
        latency = str(syscall[2])
        threadID = str(syscall[4])
        direction = str(syscall[5])
        syscall_type = str(syscall[6])
        evt_string = ""
        if len(syscall[7]) > 0:
            for evt in syscall[7]:
                evt_string = evt_string + str(evt)
        
        syscall =   rawtime + " | " +       \
                    latency + " | " +       \
                    threadID + " | " +      \
                    direction + " | " +     \
                    syscall_type + " | " +  \
                    evt_string + " | " +    \
                    str(syscall_num)

        filename = "alarm_info/raw_syscalls/raw_list_Alarm_No_" + str(self.alarm_count) 
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(filename, 'a') as raw_list:
            raw_list.write(syscall + "\n")

    def track_mv_window(self, ngram_tuple):
        """
        receive ngram_tuple write in deque
        keep moving window of demo_model
        """
        self.deque_window.append(ngram_tuple)
        if len(self.deque_window) >= self.window_length:
            self.deque_window.popleft()

    def save_tracked_window(self):
        """
        save tracked window to file
        save tracked window in queue
        ->preparation for frontend reports
        """
        window_name = "window_" + time.strftime("%I:%M:%S") + \
                        "_Alarm_No_" + str(self.alarm_count)
        filename = "alarm_info/tracked_window/" + window_name
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        for entry in self.deque_window:
            with open(filename, 'a') as window_file:
                window_file.write(''.join(str(entry) + "\n"))
            self.last_alarm_content = self.last_alarm_content + ''.join(str(entry) + "\n")
        self.last_alarm_queue.append(self.last_alarm_content)
        self.last_alarm_content = ""

    def save_current_window(self, ngram_tuple, score, mismatch_value, consecutive_alarm):
        """
        if it is a consecutive alarm save to queue 
        else save current window of ngrams to new file with timestamp
        and score as name
        """
        # if its the first ngram which exceeds the alarm threshold
        # create queue and save tracked moving window 
        if not consecutive_alarm and not ngram_tuple is None:
            self.save_tracked_window()
            self.deque_alarm = collections.deque() 
            self.deque_alarm.append([ngram_tuple, score, mismatch_value])
        elif consecutive_alarm and not ngram_tuple is None:
            # add last syscall of ngram
            self.deque_alarm.append([(ngram_tuple[len(ngram_tuple)-1]), score, mismatch_value])
        elif ngram_tuple is None:
            print("saving queue with length {} in file".format(len(self.deque_alarm)))
            print(str(self.alarm_count))
            new_filename = "alarm_info/" + \
                    str(date.today()) + "_" + \
                    time.strftime("%I:%M:%S") + "_" + \
                    "Alarm_No_" + str(self.alarm_count) + \
                    ".txt"
            with open(new_filename, "a") as f:
                for entry in self.deque_alarm:
                    f.write(
                        str(entry[0]) +
                        " " + str(entry[1]) + 
                        " " + str(entry[2]) + 
                        "\n") 
            self.alarm_count += 1

    def handle_alarm(self, ngram_tuple, score):
        """
        add ngram_tuple which triggered an alarm 
        to list of consecutive alarms
        if alarms stop, model sends consecutive=False
        :param ngram_tuple: ngram_tuple handled by ids
        :param consecutive: if consecutive ended
        """
        if ngram_tuple != None:
            self.consecutive_alarm_list.append([ngram_tuple, score])
        else:
            print("consecutive end")
            new_filename = "alarm_info/" + \
                str(date.today()) + "_" + \
                time.strftime("%I:%M:%S") + "_" + \
                ".txt"
            with open(new_filename, "a") as f:
                for ngram_tuple in self.consecutive_alarm_list:
                    f.write(
                        str(ngram_tuple[0]) + str(ngram_tuple[1])) + "\n"

    def get_last_alarm_content(self):
        if self.last_alarm_queue:
            tmp = self.last_alarm_queue.popleft()
            print(len(tmp))
            return tmp
        else:
            return ""


