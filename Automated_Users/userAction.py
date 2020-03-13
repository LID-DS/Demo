import sys
import time
import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


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

def register(driver, email, password, security_question):
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


def login(driver, email, password):
    

    #Open the website
    driver.get('http://localhost:3000/#/login')

    try:
        #get rid of pop up window by clicking in top right corner
        driver.find_element_by_xpath('//div[contains(@class,"cdk-overlay-pane")]//button[@aria-label="Close Welcome Banner"]').click()
    except:
        print("No Welcome Banner")

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
    driver.find_element_by_xpath('//div[contains(@aria-describedby, "cookieconsent:desc")]//a[@aria-label="dismiss cookie message"]').click()

def select_products(driver, selected_products, add_to_basket, leave_feedback):

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
        #if last row middle product is chosen
        #wait for popup to close (...put into basket) or else it is obscured
        if selection == 10:
            time.sleep(8)
        else: time.sleep(1)
        #select product
        basket_button = driver.find_element_by_xpath(product_path.format(products[selection][0],products[selection][1]))
        #scroll to element so it is clickable
        driver.execute_script("arguments[0].scrollIntoView();", product_button)
        if leave_feedback:
            return 0

        if add_to_basket:
            #click Put into Basket
            product_button.click()


def change_language():
    return 0

def leave_feedback():
    return 0

def get_product_basket_button(driver, product_number):

    basket_path = '//div[contains(@class, "ng-star-inserted")]//mat-grid-tile[@style="left: {}; width: calc(33.3333% - 20px); margin-top: {}; padding-top: calc(33.3333% - 20px);"]//button[@aria-label="Add to Basket"]'
    basket_button = driver.find_element_by_xpath(basket_path.format(products[product_number][0],products[product_number][1]))

    return basket_button

def get_product_feedback_field(driver, product_number):

    product_path = '//div[contains(@class, "ng-star-inserted")]//mat-grid-tile[@style="left: {}; width: calc(33.3333% - 20px); margin-top: {}; padding-top: calc(33.3333% - 20px);"]//div[@aria-label="Click for more information about the product"]'
    product_button = driver.find_element_by_xpath(product_path.format(products[product_number][0],products[product_number][1]))
    product_button.click()
    #select feedback window
    feedback_path = '//div[contains(@class, "cdk-overlay-pane")]//textarea[contains(@class, "mat-input-element")]'
    feedback_input = driver.find_element_by_xpath(feedback_path)
    return feedback_input

def put_products_in_basket(driver, selected_products):

    for selection in selected_products:
        #if last row middle product is chosen
        #wait for popup to close (...put into basket) or else it is obscured
        if selection == 10:
            time.sleep(8)
        else: time.sleep(1)
        basket_button = get_product_basket_button(driver, selection)
        #scroll to element so it is clickable
        driver.execute_script("arguments[0].scrollIntoView();", basket_button)
        basket_button.click()

def leave_feedback(driver, selected_products):
    
    for selection in selected_products:
        #get feedback field
        feedback_field = get_product_feedback_field(driver, selection)
        driver.execute_script("arguments[0].scrollIntoView();", feedback_field)
        #enter feedback
        feedback_field.send_keys('u got that juice')
        #get submit button 
        submit_path = '//div[contains(@class, "cdk-overlay-pane")]//button[contains(@aria-label, "Send the review")]'
        submit_button = driver.find_element_by_xpath(submit_path) 
        submit_button.click()
        close_path = '//div[contains(@class, "cdk-overlay-pane")]//button[contains(@aria-label, "Close Dialog")]'
        close_button = driver.find_element_by_xpath(close_path) 
        close_button.click()
        
if __name__ == "__main__":

    #credentials
    try:
        email = sys.argv[1]
    except:
        print("please enter email as argument in command")
        sys.exit() 
    password = "testpassword"
    security_question = "middlename"

    driver = webdriver.Firefox()
    

    register(driver, email, password, security_question)
    login(driver, email, password)
    time.sleep(1.5)
    
    how_many_items_in_basket = random.randint(0,10)
    random_items = []
    #TODO select random products to put in basket
    for i in range(0,how_many_items_in_basket + 1):
        random_items.append(random.randint(0,11)) 
    for item in random_items:
        put_products_in_basket(driver, [item])
        if (random.randint(0,1) > 0):
            leave_feedback(driver, [item])
