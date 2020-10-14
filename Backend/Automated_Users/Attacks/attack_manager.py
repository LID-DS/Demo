import threading

from Automated_Users.Attacks.attacks import SQLInjection, FalseJWTLogin, \
        XSSAttack, SensitiveDataExposure, RemoteCodeExecution, FileOverride
from Automated_Users.Attacks.reconnaissance import Reconnaissance


class AttackManager:
    """
    Interface for running attacks and enumeration in new thread
    """

    def __init__(self):
        """
        initialize Attacks and Enumeration
        """
        self.reconnaissance = Reconnaissance()
        self.sql_injection = SQLInjection()
        self.false_jwt = FalseJWTLogin()
        self.xss_attack = XSSAttack()
        self.sensitive_data_exposure = SensitiveDataExposure()
        self.remote_code_execution = RemoteCodeExecution()
        self.file_override = FileOverride()

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
        self.start_threaded_attack(self.false_jwt.run)

    def run_xss(self, xss_type):
        """
        start thread with new xss attack
        """
        if xss_type == 'xss simple':
            self.start_threaded_attack(
                    self.xss_attack.run("simple"))
        elif xss_type == 'xss advanced':
            self.start_threaded_attack(
                    self.xss_attack.run("advanced"))

    def run_sensitive_data_exposure(self, exposed_file_path):
        """
        there are several exposed files on the server
        -> access these files
        """
        self.start_threaded_attack(
            self.sensitive_data_exposure.run(exposed_file_path))

    def run_remote_code_execution(self, token=None, payload=None):
        """
        vulnerability in B2B api
        able to run code which keeps server busy -> regular expression
        """
        self.start_threaded_attack(
                self.remote_code_execution.run(token, payload))

    def run_file_override(self):
        """
        vulnerability in file upload at /#/complain
        able to upload zip with file traversal -> override ftp/legal.md
        """
        self.start_threaded_attack(
                self.file_override.run())

    def start_threaded_attack(
            self, attack, wait=False, attributes=None):
        """
        generic method to start attack in thread
        """
        attack_thread = threading.Thread(
                target=attack,
                args=([]))
        attack_thread.start()
        if wait:
            attack_thread.join()
