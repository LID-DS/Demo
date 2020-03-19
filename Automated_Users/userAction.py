import sys
import time
import random
import threading
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

class User:
    
    def __init__(self, email, password, security_question): 
        self.driver = webdriver.Firefox()
        self.email = email
        self.password = password
        self.security_question = security_question   

    def register(self):
        #Open the website
        self.driver.get('http://localhost:3000/#/register')
        try:
            #get rid of pop up window by clicking in top right corner
            self.driver.find_element_by_xpath('//div[contains(@class,"cdk-overlay-pane")]//button[@aria-label="Close Welcome Banner"]').click()
        except:
            print('No Welcome Banner')
        #find email box
        reg_email_box = self.driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="emailControl"]')
        reg_email_box.send_keys(self.email)
        #find password box
        reg_password_box = self.driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="passwordControl"]')
        reg_password_box.send_keys(self.password)
        #find repeat password box
        reg_password_repeat_box = self.driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="repeatPasswordControl"]')
        reg_password_repeat_box.send_keys(self.password)
        #select security question
        self.driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//mat-select[@id="mat-select-0"]').click()
        self.driver.find_element_by_xpath('//div[contains(@id, "cdk-overlay-2")]//mat-option[@id="mat-option-0"]').click()
        #answer security question
        security_answer_box = self.driver.find_element_by_xpath('//div[contains(@id, "registration-form")]//input[@id="securityAnswerControl"]')
        security_answer_box.send_keys(self.security_question)
        #click registration button
        self.driver.find_element_by_id('registerButton').click()


    def login(self):
        
        print('Try logging in')
        #Open the website
        self.driver.get('http://localhost:3000/#/login')

        try:
            #get rid of pop up window by clicking in top right corner
            self.driver.find_element_by_xpath('//div[contains(@class,"cdk-overlay-pane")]//button[@aria-label="Close Welcome Banner"]').click()
        except:
            print("No welcome banner")

        #Login with given credentials
        #find email box
        email_box = self.driver.find_element_by_name('email')
        #enter email address
        email_box.send_keys(self.email)
        #find password box
        pass_box = self.driver.find_element_by_name('password')
        #enter password
        pass_box.send_keys(self.password)
        #find login button
        login_button = self.driver.find_element_by_xpath('//div[contains(@id, "login-form")]//button[@id="loginButton"]')
        #click button
        login_button.click()
        time.sleep(1)
        #remove cookie overlay window
        try:
            self.driver.find_element_by_xpath('//div[contains(@aria-describedby, "cookieconsent:desc")]//a[@aria-label="dismiss cookie message"]').click()
        except:
            print('No cookie banner')


    def logout(self):
    
        print('Logout')
        account_button = self.driver.find_element_by_id('navbarAccount')
        account_button.click()
        logout_button = self.driver.find_element_by_id('navbarLogoutButton')
        logout_button.click()

    def select_products(self, selected_products, add_to_basket, leave_feedback):

        product_path = '//div[contains(@class, "ng-star-inserted")]//mat-grid-tile[@style="left: {}; width: calc(33.3333% - 20px); margin-top: {}; padding-top: calc(33.3333% - 20px);"]//button[@aria-label="Add to Basket"]'
        for selection in selected_products:
            #if last row middle product is chosen
            #wait for popup to close (...put into basket) or else it is obscured
            if selection == 10:
                time.sleep(8)
            else: time.sleep(1)
            #select product
            basket_button = self.driver.find_element_by_xpath(product_path.format(products[selection][0],products[selection][1]))
            #scroll to element so it is clickable
            self.driver.execute_script("arguments[0].scrollIntoView();", product_button)
            if leave_feedback:
                return 0

            if add_to_basket:
                #click Put into Basket
                product_button.click()

    def change_language(self):
        return 0

    def get_product_basket_button(self, product_number):
        basket_path = '//div[contains(@class, "ng-star-inserted")]//mat-grid-tile[@style="left: {}; width: calc(33.3333% - 20px); margin-top: {}; padding-top: calc(33.3333% - 20px);"]//button[@aria-label="Add to Basket"]'
        basket_button = self.driver.find_element_by_xpath(basket_path.format(products[product_number][0],products[product_number][1]))

        return basket_button

    def get_product_feedback_field(self, product_number):
        product_path = '//div[contains(@class, "ng-star-inserted")]//mat-grid-tile[@style="left: {}; width: calc(33.3333% - 20px); margin-top: {}; padding-top: calc(33.3333% - 20px);"]//div[@aria-label="Click for more information about the product"]'
        product_button = self.driver.find_element_by_xpath(product_path.format(products[product_number][0],products[product_number][1]))
        product_button.click()
        #select feedback window
        feedback_path = '//div[contains(@class, "cdk-overlay-pane")]//textarea[contains(@class, "mat-input-element")]'
        feedback_input = self.driver.find_element_by_xpath(feedback_path)
        return feedback_input

    def put_products_in_basket(self, selected_products):
        for selection in selected_products:
            #if last row middle product is chosen
            #wait for popup to close (...put into basket) or else it is obscured
            if selection == 10:
                time.sleep(8)
            else: time.sleep(1)
            basket_button = self.get_product_basket_button(selection)
            #scroll to element so it is clickable
            self.driver.execute_script("arguments[0].scrollIntoView();", basket_button)
            basket_button.click()

    def leave_feedback(self, selected_products):
        for selection in selected_products:
            #get feedback field
            feedback_field = self.get_product_feedback_field(selection)
            self.driver.execute_script("arguments[0].scrollIntoView();", feedback_field)
            #enter feedback
            feedback_field.send_keys('u got that juice')
            #get submit button 
            submit_path = '//div[contains(@class, "cdk-overlay-pane")]//button[contains(@aria-label, "Send the review")]'
            submit_button = self.driver.find_element_by_xpath(submit_path) 
            submit_button.click()
            close_path = '//div[contains(@class, "cdk-overlay-pane")]//button[contains(@aria-label, "Close Dialog")]'
            close_button = self.driver.find_element_by_xpath(close_path) 
            close_button.click()

    def go_shopping(self):

        print("Go shopping")
        # choose how many items user puts in basket
        how_many_items_in_basket = random.randint(0,2)
        random_items = []
        # randomly select what items are chosen 
        # with p=0.5 leave feedback of chosen product
        for i in range(0,how_many_items_in_basket + 1):
            random_items.append(random.randint(0,11)) 
        for item in random_items:
            print("Put item into basket")
            self.put_products_in_basket([item])
            if (random.randint(0,1) > 0):
                print("Leave Feedback")
                self.leave_feedback([item])
            
    def action(self):
        
        self.register()
        for i in range(2):
            self.login()
            time.sleep(1.5)
            self.go_shopping()
            self.logout()


if __name__ == "__main__":
    
    parallel_users = 2

    #credentials
    users = []
    password = "testpassword"
    security_question = "middlename"
    # random addition so not using same email while debugging
    random_addition = random.randint(0,9999999999)
    
    #create user objects
    for no_use in range(parallel_users):
        email = "testmail{}{}@test.de".format(no_use, random_addition) 
        users.append(User(email, password, security_question)) 

    i = 0
    for user in users:
        print('start surfing user: {}'.format(i))
        i += 1
        user_thread = threading.Thread(target=user.action, args=([]))
        user_thread.start()

