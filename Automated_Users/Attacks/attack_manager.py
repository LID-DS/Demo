import threading

from Automated_Users.Attacks.sql_get_user_credentials import SQLInjection
from Automated_Users.Attacks.reconnaissance import Reconnaissance


class AttackManager:

    def __init__(self):
        """
        initialize sql injection and reconnaissance
        """
        self.sql_injection = SQLInjection(
                base_url="http://localhost:3000")
        self.reconnaissance = Reconnaissance()

    def run_sql_injection(self, info):
        """
        run sql injection in new thread
        -> either try hard with trial and error of finding right attack vector
        -> or just run sql injection with prepared injection
        """
        if info == 'try hard':
            attack_thread = threading.Thread(
                            target=self.sql_injection.run_tryhard,
                            args=([]))
        else:
            attack_thread = threading.Thread(
                            target=self.sql_injection.run,
                            args=([]))
        attack_thread.start()

    def run_enum(self):
        """
        start thread running dirb http enumeration
        :returns 1 when enumeration is done
        """
        enum_thread = threading.Thread(
                target=self.reconnaissance.run_enum(),
                args=([]))
        enum_thread.start()
        # wait for enumeration to finish 
        enum_thread.join()
        return 1
        
