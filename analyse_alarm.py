from datetime import date
import shutil
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

    def track_mv_window(self, ngram_tuple):
        """
        receive ngram_tuple write in deque
        keep moving window of demo_model
        """
        self.deque_window.append(ngram_tuple)
        if len(self.deque_window) >= self.window_length:
            self.deque_window.popleft()

    def save_current_window(self, score, mismatch_value):
        """
        save current window of ngrams to new file with timestamp
        and score as name
        """
        new_filename = "alarm_info/" + \
                str(date.today()) + "_" + \
                time.strftime("%I:%M:%S") + "_" + \
                str(score).replace('.', '') + \
                ".txt"
        with open(new_filename, "a") as f:
            for ngram_tuple in self.deque_window:
                f.write(
                    self.ids._ngram_tuple_to_str(ngram_tuple) + 
                    " " + str(mismatch_value) + 
                    "\n") 

    def handle_alarm(self,
            ngram_tuple,
            consecutive_end,
            score,
            mismatch_value):
        """
        add ngram_tuple which triggered an alarm 
        to list of consecutive alarms
        if alarms stop, model sends consecutive=False
        :param ngram_tuple: ngram_tuple handled by ids
        :param consecutive: if consecutive ended
        """
        if consecutive_end:
            self.consecutive_alarm_list.append(ngram_tuple)
        else:
            new_filename = "alarm_info/" + \
                str(date.today()) + "_" + \
                time.strftime("%I:%M:%S") + "_" + \
                str(score).replace('.', '') + \
                ".txt"
            with open(new_filename, "a") as f:
                for ngram_tuple in self.consecutive_alarm_list:
                    f.write(
                        self.ids._ngram_tuple_to_str(ngram_tuple) +
                        " " + str(mismatch_value) +
                        "\n")


