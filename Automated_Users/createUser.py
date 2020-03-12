import sys
import time
from selenium import webdriver



def register(email, password, security_question):

#Open the website
    driver.get('http://localhost:3000/#/register')

#get rid of pop up window by clicking in top right corner
    driver.find_element_by_xpath('//div[contains(@class,"cdk-overlay-pane")]//button[@aria-label="Close Welcome Banner"]').click()

#find email box
    reg_email_box = driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="emailControl"]')
#reg_email_box = driver.find_element_by_name('emailControl')
    reg_email_box.send_keys(email)

#find password box
    reg_password_box = driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="passwordControl"]')
#reg_password_box= driver.find_element_by_name('passwordControl')
    reg_password_box.send_keys(password)
#find repeat password box
    reg_password_repeat_box = driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="repeatPasswordControl"]')
    reg_password_repeat_box.send_keys(password)

#select security question
    driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//mat-select[@id="mat-select-0"]').click()

    driver.find_element_by_xpath('//div[contains(@id, "cdk-overlay-2")]//mat-option[@id="mat-option-0"]').click()

#answer security question
    security_answer_box = driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="securityAnswerControl"]')
    security_answer_box.send_keys(security_question)

#click registration button
    driver.find_element_by_id('registerButton').click()


def login(email, password):
#Login with given credentials
#find email box
    email_box = driver.find_element_by_name('email')
#enter email address
    email_box.send_keys(email)
#find password box
    pass_box = driver.find_element_by_name('password')
#enter password
    pass_box.send_keys(password)
#find login button
    login_button = driver.find_element_by_xpath('//div[contains(@id, "login-form")]//button[@id="loginButton"]')
#click button
    login_button.click()
    time.sleep(1)
#remove cookie overlay window
    #cookie_button = driver.find_element_by_xpath('//div[contains(@aria-live, "polite")]//div[@class="cc-compilance"]')

def select_products(selected_products):

#list of possible products to put in basket
    products = [
        ["0px", "0px"],
        ["calc(33.3333% + 10px)", "0px"],
        ["calc(66.6667% + 20px)", "0px"],
        ["0px", "calc(33.3333% + 10px)"],
        ["calc(33.3333% + 10px)", "calc(33.3333% + 10px)"],
        ["calc(66.6667% + 20px)", "calc(33.3333% + 10px)"],
        ["0px", "calc(66.6667% + 20px)"],
        ["calc(33.3333% + 10px)", "calc(66.6667% + 20px)"],
        ["calc(66.6667% + 20px)", "calc(66.6667% + 20px)"],
        ["0px", "calc(100% + 30px)"],
        ["calc(33.3333% + 10px)", "calc(100% + 30px)"],
        ["calc(66.6667% + 20px)", "calc(100% + 30px)"],
    ]

    product_path = '//div[contains(@class, "ng-star-inserted")]//mat-grid-tile[@style="left: {}; width: calc(33.3333% - 20px); margin-top: {}; padding-top: calc(33.3333% - 20px);"]//button[@aria-label="Add to Basket"]'

    for selection in selected_products:
        #if selected item is not in first row, scroll down
        if(selection > 2):
            print("scroll")
        driver.find_element_by_xpath(product_path.format(products[selection][0],products[selection][1])).click()
        time.sleep(1)


if __name__ == "__main__":

    driver = webdriver.Firefox()
#credentials
    email = sys.argv[1]
    password = "testpassword"
    security_question = "middlename"

    register(email, password, security_question)
    login(email, password)
    time.sleep(1.5)
    #TODO select random products to put in basket
    #TODO scroll down window if product on bottom of page was chosen
    select_products([0,1,2,3,4])#,4,5,6,7,8,9,10,11])


