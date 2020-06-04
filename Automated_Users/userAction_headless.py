import sys
import time
import random
import threading
import os 
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
 

MAX_LOGOUT_FAILS = 5
MAX_USERS = 4

class User:
    
    def __init__(self, email, password, security_question, user_number, visible=False): 
        #configurations for headless browsing
        self.chrome_options = Options()
        if not visible: 
            #no Browser window
            self.chrome_options.add_argument("--headless")
        else:
            #needs to be in full screen  
            self.chrome_options.add_argument("--kiosk")
        self.chrome_options.add_argument("--window-size=1480,996")
        # needed for running as root
        self.chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.email = email
        self.password = password
        self.security_question = security_question   
        self.user_number = user_number
        self.logout_count = 0
        #to stop thread
        self.is_running = True
        #to see if thread has stopped
        self.is_finished = False

    def reset(self):
        self.__init__(self.email, self.password, self.security_question, self.user_number)
    
    def register(self):
        #Open the website
        self.driver.get('http://localhost:3000/#/register')
        try:
            #get rid of pop up window by clicking in top right corner
            self.driver.find_element_by_xpath('//div[contains(@class,"cdk-overlay-pane")]//button[@aria-label="Close Welcome Banner"]').click()
        except:
            pass
        #find email box
        reg_email_box = self.driver.find_element_by_xpath(
                '//div[contains(@id, "registration-form")]//input[@id="emailControl"]')
        reg_email_box.send_keys(self.email)
        #find password box
        reg_password_box = self.driver.find_element_by_xpath(
                '//div[contains(@id, "registration-form")]//input[@id="passwordControl"]')
        reg_password_box.send_keys(self.password)
        #find repeat password box
        reg_password_repeat_box = self.driver.find_element_by_xpath(
                '//div[contains(@id, "registration-form")]//input[@id="repeatPasswordControl"]')
        reg_password_repeat_box.send_keys(self.password)
        #occasional overlapping without sleep
        time.sleep(1)
        #select security question
        self.driver.find_element_by_xpath(
                '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-register/div/mat-card/div[2]/div[1]/mat-form-field[1]/div/div[1]/div[3]').click()
        self.driver.find_element_by_xpath(
                '//div[contains(@id, "cdk-overlay-2")]//mat-option[@id="mat-option-0"]').click()
        #answer security question
        security_answer_box = self.driver.find_element_by_xpath(
                '//div[contains(@id, "registration-form")]//input[@id="securityAnswerControl"]')
        security_answer_box.send_keys(self.security_question)
        #click registration button
        self.driver.find_element_by_id('registerButton').click()


    def login(self):
        
        #print("User: " + str(self.user_number) + " " + 'Try logging in')
        #Open the website
        self.driver.get('http://localhost:3000/#/login')

        try:
            #get rid of pop up window by clicking in top right corner
            self.driver.find_element_by_xpath('//div[contains(@class,"cdk-overlay-pane")]//button[@aria-label="Close Welcome Banner"]').click()
        except:
            pass
            #print("User: " + str(self.user_number) + " " + 'No Welcome Banner')

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
        #logout count for too many failed logouts
        self.logout_count = 0
        #remove cookie overlay window
        try:
            self.driver.find_element_by_xpath('//div[contains(@aria-describedby, "cookieconsent:desc")]//a[@aria-label="dismiss cookie message"]').click()
        except:
            #print("User: " + str(self.user_number) + " " + 'No cookie banner')
            pass


    def logout(self):
     
        #print("User: " + str(self.user_number) + " " + 'Logout')
        self.logout_count += 1
        if (self.logout_count < MAX_LOGOUT_FAILS):
            try:    
                account_button = self.driver.find_element_by_id('navbarAccount')
                account_button.click()
                logout_button = self.driver.find_element_by_id('navbarLogoutButton')
                logout_button.click()
            except:
                #print("User: " + str(self.user_number) + " " + "Logout failed, retrying")
                self.reload()
                self.logout()
        else:
            #print("User: " + str(self.user_number) + " " + 'max retries for relogin reached \n reinitialize User')
            self.driver.quit()
            self.reset()
            

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

        product_paths = "/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-search-result/div/div/div[2]/mat-grid-list/div/mat-grid-tile[{}]/figure/mat-card/div[{}]/button"
        # product 7,9,11 have extra banner, so different xpath 
        if product_number in [7,9,11]:
            extra_info = 3
        else:
            extra_info = 2
        basket_button = self.driver.find_element_by_xpath(product_paths.format(product_number + 1, extra_info))
        return basket_button

    def get_product_feedback_field(self, product_number):
        product_path = '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-search-result/div/div/div[2]/mat-grid-list/div/mat-grid-tile[{}]/figure/mat-card/div[{}]' 
        
        # product 7,9,11 have extra banner -> different xpath
        if product_number in [7,9,11]:
            extra_info = 2
        else: 
            extra_info = 1
        try: 
            product_button = self.driver.find_element_by_xpath(product_path.format(product_number + 1, extra_info))
            product_button.click()
        except:
            return None

        try:
            #select feedback window
            feedback_path = '//div[contains(@class, "cdk-overlay-pane")]//textarea[contains(@class, "mat-input-element")]'
            feedback_input = self.driver.find_element_by_xpath(feedback_path)
        except:
            print("Error finding feedback field")
            return None
        return feedback_input

    def put_products_in_basket(self, selected_products):

        for selection in selected_products:
            #if last row middle product is chosen
            #wait for popup to close (...put into basket) or else it is obscured
            if selection == 10:
                time.sleep(8)
            else: time.sleep(1)
            try: 
                basket_button = self.get_product_basket_button(selection)
                #scroll to element so it is clickable
                self.driver.execute_script("arguments[0].scrollIntoView();", basket_button)
                basket_button.click()
            except:
                #print("User: " + str(self.user_number) + " " + "Error putting item into basket -> skipping item")
                self.logout()
                time.sleep(1)
                self.login()

    def leave_feedback(self, selected_products):

        for selection in selected_products:
            #get feedback field
            feedback_field = self.get_product_feedback_field(selection)
            if feedback_field == None:
                #print("User: " + str(self.user_number) + " " + "Error leaving feedback -> skipping feedback")
                return
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

    def go_shopping(self, max_products):

        #print("User: " + str(self.user_number) + " " + "Go shopping")
        # choose how many items user puts in basket
        how_many_items_in_basket = random.randint(0,max_products)
        random_items = []
        # randomly select what items are chosen 
        # with p=0.5 leave feedback of chosen product
        for i in range(0,how_many_items_in_basket + 1):
            random_items.append(random.randint(0,11)) 
        for item in random_items:
            if not self.is_running: 
                self.is_finished = True
                return 
            #print("User: " + str(self.user_number) + " " + "Put item into basket")
            self.put_products_in_basket([item])
            if (random.randint(0,4) >  2):
                self.reload()
            if (random.randint(0,1) > 0):
                #print("User: " + str(self.user_number) + " " + "Leave Feedback")
                self.leave_feedback([item])

    def reload(self):
        self.driver.refresh()
            
    def action(self):
        """
        register and 
        loop
        --> login user
        --> go shopping(includes leaving feedback) 
        --> logout
        """
        # -->
        self.register()
        time.sleep(0.1)
        while(self.is_running):
            if not self.is_running: 
                self.is_finished = True
                self.driver.quit()
                return 
            # -->
            self.login()
            time.sleep(1.5)
            # -->
            # includes leaving feedback
            self.go_shopping(max_products=10)
            time.sleep(1)
            # -->
            self.logout()
            if (random.randint(0,10) > 1):
                for i in range(0,10):
                    if not self.is_running:
                        self.is_finished = True
                        self.driver.quit()
                        break
                    time.sleep(1)
            if (random.randint(0,3) > 1):
                self.driver.quit()
                if not self.is_running:
                    self.is_finished = True    
                    self.driver.quit()
                    break
                time.sleep(5)
                self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.quit()
        #wait for last actions, then set true so we know thread has finished
    
    def suicide(self):
        """
        stop user
        """
        self.is_running = False

        
class UserManager:
    
    def __init__(self):
        self.active_users = []
        self.active_threads = []   
        self.training_running = False 
    
    def checkSite(self):
        """
        check if juice-shop is online 
        """
        site_offline = True
        while site_offline:
            try:
                requests.get('http://localhost:3000')
                site_offline=False
            except:
                print("Juice Shop is offline") 
            time.sleep(5)
    
    def add_user(self, visible=False): 
        """
        create user with email, password, security question
        """
        if(len(self.active_users) >= MAX_USERS):
            print("MAX_USERS reached")
            return
        self.checkSite()
        password = "testpassword"
        security_question = "middlename"
        email = "mail{}{}@test.com".format(len(self.active_users), random.randint(0,9999999999)) 
        new_user = User(email, password, security_question, user_number=len(self.active_users), visible=visible)
        self.active_users.append(new_user)
        print("User: {} was added".format(new_user.user_number))
        try:    
            user_thread = threading.Thread(target=new_user.action, args=([]))
            user_thread.start()
        except Exception:
            print("Error starting user action")
        #self.active_threads.append(user_thread)

    def remove_user(self):
        """
        set is_running Flag to false to stop userActions and end the thread
        remove user from active user list
        """
        #get last user of list 
        if(len(self.active_users) < 1):
            print("No active users")
            return
        user = self.active_users[len(self.active_users) - 1]
        print("User: {} was removed".format(user.user_number))
        user.suicide()
        self.active_users = self.active_users[:-1]
        return user 

    def remove_all_user(self):
        for i in range(0,len(self.active_users)):
            self.active_users[i].suicide()
        self.active_users = []

    def show_actions(self):
        return 0
        #run user which is not headless

    def start_training_sequence(self):
        """
        automated sequence of adding & removing users
        loop until stop_sequence button is pressed
            add a random number[1:MAX_USERS] of users
            delete random number of users
        """
        self.training_running = True
        while(self.training_running):
            # add users, but never more than MAX_USERS
            diff_to_MAX_USERS = MAX_USERS - len(self.active_users)
            for i in range(0,random.randint(1,diff_to_MAX_USERS)):
                self.add_user()
            if not self.training_running:
                break
            time.sleep(15)
            # remove random number of users 
            random_count = random.randint(1,len(self.active_users))  
            for j in range(0,random_count):
                self.remove_user()
            if not self.training_running:
                break
            time.sleep(15)
        self.remove_all_user()
        
if __name__ == "__main__":
    userManager = UserManager()
    userManager.add_user(True)
    userManager.add_user(True)
    time.sleep(3)
    userManager.remove_user()
    time.sleep(3)
    userManager.remove_user()
