from datetime import date
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
        self.file_count = 0

    def track_mv_window(self, ngram_tuple):
        """
        receive ngram_tuple write in deque
        keep moving window of demo_model
        """
        self.deque_window.append(ngram_tuple)
        if len(self.deque_window) >= self.window_length:
            self.deque_window.popleft()

# def save_current_window(self, ngram_tuple, score, mismatch_value, consecutive_alarm):
#        """
#        save current window of ngrams to new file with timestamp
#        and score as name
#        """
#        new_filename = "alarm_info/" + \
#                str(date.today()) + "_" + \
#                time.strftime("%I:%M:%S") + "_" + \
#                str(score).replace('.', '') + \
#                ".txt"
#        with open(new_filename, "a") as f:
#            for ngram_tuple in self.deque_window:
#                f.write(
#                    self.ids._ngram_tuple_to_str(ngram_tuple) + 
#                    " " + str(mismatch_value) + 
#                    "\n") 

    def save_current_window(self, ngram_tuple, score, mismatch_value, consecutive_alarm):
        """
        save current window of ngrams to new file with timestamp
        and score as name
        """
        if not consecutive_alarm and not ngram_tuple is None:
            self.deque_window = collections.deque() 
            self.deque_window.append([ngram_tuple, score, mismatch_value])
        elif consecutive_alarm and not ngram_tuple is None:
            # add last syscall of ngram
            if mismatch_value == 1:
                self.deque_window.append([(ngram_tuple[len(ngram_tuple)-1]), score])
        if ngram_tuple is None:
            new_filename = "alarm_info/" + \
                    str(date.today()) + "_" + \
                    time.strftime("%I:%M:%S") + "_" + \
                    str(self.file_count) + \
                    ".txt"
            self.file_count += 1
            with open(new_filename, "a") as f:
                for entry in self.deque_window:
                    f.write(
                        str(entry[0]) +
                        " " + str(entry[1]) + 
                        "\n") 

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
                str(self.file_count) + \
                ".txt"
            self.file_count += 1
            with open(new_filename, "a") as f:
                for ngram_tuple in self.consecutive_alarm_list:
                    f.write(
                        str(ngram_tuple[0]) + str(ngram_tuple[1]) +#self.ids._ngram_tuple_to_str(ngram_tuple) +
                        "\n")


