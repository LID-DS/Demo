from selenium import webdriver

username = "testname"
password = "testpassword"

#Before using add geckodriver path with:
# export PATH=$PATH: .../Demo/Automated_Users/Gecko_Driver/
#Using Chrome to access web
driver = webdriver.Firefox()

#Login with given credentials

#Open the website
driver.get('http://localhost:3000/#/login')

#get rid of pop up window by clicking in top right corner
driver.find_element_by_xpath('//div[contains(@class,"cdk-overlay-pane")]//button[@aria-label="Close Welcome Banner"]').click()

#find email box
email_box = driver.find_element_by_name('email')

#enter email address
email_box.send_keys(username)

#find password box
pass_box = driver.find_element_by_name('password')

#enter password
pass_box.send_keys(password)

#find login button
login_button = driver.find_element_by_name('loginButton')

#click button
login_button.click()
