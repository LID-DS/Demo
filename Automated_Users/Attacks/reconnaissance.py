import subprocess
import os
import re


class Reconnaissance:

    def __init__(self):
        """
        Initialize dirb subprocess in new thread
        use standard dictionary of dirb
        """

    def run_enum(self):
        command="dirb http://localhost:3000/"
        os.system("gnome-terminal -e 'bash -c \""+command+";bash\"'")
