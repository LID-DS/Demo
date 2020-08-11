from datetime import date
import os
import time
import collections
import data_handling

class Analysis:
    """
    keep track of current syscall window and handle syscall which
    triggered an alarm
    """

    def __init__(self, window_length, ids):
        """
        """
        self.window_length = window_length
        self.deque_window = collections.deque()
        self.ids = ids
        self.consecutive_alarm_list = []
        self.alarm = False
        self.alarm_count = 0

    def save_raw_syscall(self, syscall, syscall_num):
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
        save window to file
        """
        for entry in self.deque_window:
            window_name = "window_" + time.strftime("%I:%M:%S") + \
                            "Alarm_No_" + str(self.alarm_count)
            filename = "alarm_info/tracked_window/" + window_name
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(filename, 'a') as window_file:
                window_file.write(''.join(str(entry) + "\n"))

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
            #if mismatch_value == 1:
            self.deque_alarm.append([(ngram_tuple[len(ngram_tuple)-1]), score, mismatch_value])
        if ngram_tuple is None:
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
                        str(ngram_tuple[0]) + str(ngram_tuple[1]) +#self.ids._ngram_tuple_to_str(ngram_tuple) +
                        "\n")


