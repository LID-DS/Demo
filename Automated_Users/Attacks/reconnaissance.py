import subprocess
import re


class Reconnaissance:

    def __init__(self):
        """
        Initialize dirb subprocess in new thread
        use standard dictionary of dirb
        """
        self.enum_process = subprocess.Popen(
                ['dirb', 'http://localhost:3000/',
                '/usr/share/dirb/wordlists/common.txt'],
                stdout=subprocess.PIPE)

    def run_enum(self):
        directories = []
        with self.enum_process as dirb:
            for line in dirb.stdout:
                directories.append(line)
        #split = " "
        #result_string = split.join(directories)
        #print(re.findall(".\w\+\s.*", result_string))
