import threading

from Automated_Users.Attacks.attacks import SQLInjection, FalseJWTLogin, XSSAttack
from Automated_Users.Attacks.reconnaissance import Reconnaissance


class AttackManager:

    def __init__(self):
        """
        initialize sql injection and reconnaissance
        """
        self.sql_injection = SQLInjection(
                base_url="http://localhost:3000")
        self.reconnaissance = Reconnaissance()
        self.false_jwt = FalseJWTLogin()
        self.xss_attack = XSSAttack()

    def run_sql_injection(self, info):
        """
        run sql injection in new thread
        -> either try hard with trial and error of finding right attack vector
        -> or just run sql injection with prepared injection
        """
        if info == 'try hard sql':
            self.start_threaded_attack(self.sql_injection.run_tryhard)
        else:
            self.start_threaded_attack(self.sql_injection.run)

    def run_enum(self):
        """
        start thread running dirb http enumeration
        wait for thread to finish
        :returns 1 when enumeration is done
        """
        self.start_threaded_attack(self.reconnaissance.run_enum(), wait=True)
        return 1
    
    def run_false_jwt_login(self):
        """
        start thread which tries to login as non existing user
        using sql injection to recieve false JSON Web Token 
        """
        self.start_threaded_attack(self.false_jwt.run_attack)
        
    def run_xss(self, xss_type):
        """
        start thread with new xss attack
        """
        self.start_threaded_attack(self.xss_attack.run_simple())


    def start_threaded_attack(self, attack, wait=False, attributes=None):
        """
        generic method to start attack in thread
        """
        attack_thread = threading.Thread(
                target=attack,
                args=([]))
        attack_thread.start()
        if wait:
            attack_thread.join()

