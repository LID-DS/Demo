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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
 

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
        self.driver.delete_all_cookies()
        self.email = email
        self.password = password
        self.security_question = security_question   
        self.user_number = user_number
        self.logout_count = 0
        # to stop thread
        self.is_running = True
        # to see if thread has stopped
        self.is_finished = False
        # relative directory path
        self.dirname = os.path.abspath(os.curdir)
        # feedback xpath changing when next item clicked starts with 3
        self.feedback_path_count = 3

    def reset(self):
        self.__init__(self.email, self.password, self.security_question, self.user_number)
    
    def register(self):

        #Open the website
        self.driver.get('http://localhost:3000/#/register')
        time.sleep(2)
        try:
            #get rid of pop up window 
            self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/mat-dialog-container/app-welcome-banner/div/div[2]/button[2]').click()
        except:
            print("User " + str(self.user_number) + ": Error removing welcome banner")
            #rerun registration process 
            if random.randint(0,1) >= 1:
                self.register()
            else: 
                print("User " + str(self.user_number) + ": Error removing welcome banner -> not retrying")
                return
        try: 
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
        except:
            print("User " + str(self.user_number) + ": Error entering email")
            return
        #select security question
        try:
            self.driver.find_element_by_xpath(
                '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-register/div/mat-card/div[2]/div[1]/mat-form-field[1]/div/div[1]/div[3]').click()
            self.driver.find_element_by_xpath(
                '//div[contains(@id, "cdk-overlay-2")]//mat-option[@id="mat-option-0"]').click()
        except:
            print("Error selecting security question")
            #rerun registration process
            self.register()
        security_answer_box = self.driver.find_element_by_xpath(
                '//div[contains(@id, "registration-form")]//input[@id="securityAnswerControl"]')
        security_answer_box.send_keys(self.security_question)
        try:
            #click registration button
            self.driver.find_element_by_id('registerButton').click()
        except:
            print("Error clicking register button")
            #rerun registration process
            self.register()
            pass
        return True


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
        try:
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
            try:
                login_button.click()
            except NoSuchElementException:
                print("User {}: login_button not found".format(self.user_number))
                return False
            time.sleep(1)
            #logout count for too many failed logouts
            self.logout_count = 0
        except NoSuchElementException:
            print("User {}: Login failed".format(self.user_number))
            return False
        #remove cookie overlay window
        try:
            self.driver.find_element_by_xpath('//div[contains(@aria-describedby, "cookieconsent:desc")]//a[@aria-label="dismiss cookie message"]').click()
        except:
            #print("User: " + str(self.user_number) + " " + 'No cookie banner')
            pass
        return True


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

        #product_path = '//div[contains(@class, "ng-star-inserted")]//mat-grid-tile[@style="left: {}; width: calc(33.3333% - 20px); margin-top: {}; padding-top: calc(33.3333% - 20px);"]//button[@aria-label="Add to Basket"]'
        product_path = '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-search-result/div/div/div[2]/mat-grid-list/div/mat-grid-tile[{}]/figure/mat-card/div[2]/button'
        for selection in selected_products:
            #if last row middle product is chosen
            #wait for popup to close (...put into basket) or else it is obscured
            if selection == 10:
                time.sleep(8)
            else: time.sleep(1)
            #select product
            #basket_button = self.driver.find_element_by_xpath(product_path.format(products[selection][0]))#,products[selection][1]))
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
        if product_number in [7,9,10]:
            extra_info = 3
        else:
            extra_info = 2
        basket_button = self.driver.find_element_by_xpath(product_paths.format(product_number + 1, extra_info))
        return basket_button

    def get_product_feedback_field(self, product_number):

        # product 7,9,10 have extra banner -> different xpath
        if product_number in [7,9,10]:
            extra_info = 2
        else: 
            extra_info = 1
        product_path = f'/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-search-result/div/div/div[2]/mat-grid-list/div/mat-grid-tile[{product_number + 1}]/figure/mat-card/div[{extra_info}]' 
        try: 
            product_button = self.driver.find_element_by_xpath(product_path)
            product_button.click()
        except:
            print(f"Error clicking Item {product_number} to extract feedback text area")
            return None

        try:
            #select feedback window
            #feedback_path = '//*[@id="mat-input-{}"]'
            feedback_path = "//textarea[@aria-label='Text field to review a product']"
            feedback_input = self.driver.find_element_by_xpath(feedback_path)
            self.feedback_path_count += 1
        except:
            print("Error finding feedback field")
            return None
        return feedback_input

    def put_products_in_basket(self, selected_products):

        for selection in selected_products:
            #if last row middle product is chosen
            if selection == 10:
                #wait for popup to close or else it is obscured
                time.sleep(8)
            else: time.sleep(1)
            try: 
                basket_button = self.get_product_basket_button(selection)
                #scroll to element so it is clickable
                self.driver.execute_script("arguments[0].scrollIntoView();", basket_button)
                basket_button.click()
            except:
                print(f"User {self.user_number}: Error putting item {selection} into basket -> skipping item")
                self.logout()
                time.sleep(1)
                self.login()

    def leave_feedback(self, selected_products):

        for selection in selected_products:
            #get feedback field
            feedback_field = self.get_product_feedback_field(selection)
            if feedback_field == None:
                print("User " + str(self.user_number) + ": " + "Error leaving feedback -> skipping feedback")
                return
            #self.driver.execute_script("arguments[0].scrollIntoView();", feedback_field)
            time.sleep(3)
            #enter feedback
            feedback_field.send_keys('u got that juice')
            #get submit button 
            submit_path = '//div[contains(@class, "cdk-overlay-pane")]//button[contains(@aria-label, "Send the review")]'
            submit_button = self.driver.find_element_by_xpath(submit_path) 
            submit_button.click()
            close_path = '//div[contains(@class, "cdk-overlay-pane")]//button[contains(@aria-label, "Close Dialog")]'
            close_button = self.driver.find_element_by_xpath(close_path) 
            close_button.click()

    def complain(self, file_path="/Files/test_receipt.zip"):

        print("User " + str(self.user_number) + ": complaining")
        file_path = self.dirname + file_path
        self.driver.get('http://localhost:3000/#/complain')
        feedback_textarea = self.driver.find_element_by_xpath('//*[@id="complaintMessage"]')
        feedback_textarea.send_keys("I hate your products.")
        time.sleep(2)
        input_file_path = self.driver.find_element_by_xpath('//*[@id="file"]')
        input_file_path.send_keys(file_path)
        time.sleep(2)
        self.driver.find_element_by_xpath(
            '//*[@id="submitButton"]').click()
        time.sleep(2)

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
            # dont continue if user should not run
            if not self.is_running: 
                self.clean_up_and_quit(user_manager)
                return 
            #print("User: " + str(self.user_number) + " " + "Put item into basket")
            self.put_products_in_basket([item])
            if (random.randint(0,4) >  2):
                self.reload()
            if (random.randint(0,4) == 4):
                print("User {}: Leaving feedback for item {}".format(self.user_number, item))
                self.leave_feedback([item])

    def checkout(self):
        
        basket_button = self.driver.find_element_by_xpath(
                '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-navbar/mat-toolbar/mat-toolbar-row/button[4]')
        basket_button.click()
        try: 
            #TODO test not working
            #wait for basket to load
            time.sleep(5)
            checkout_button = self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-basket/mat-card/button')
            checkout_button.click()
        except NoSuchElementException:
            print("User " + str(self.user_number) + ": has nothing in cart to checkout")
            return
        # check if address has to be added -> check if radiobutton for address exists
        try:
            time.sleep(2)
            self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-select/div/app-address/mat-card/mat-table/mat-row/mat-cell[1]/mat-radio-button').click()
            address_radio_button = self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-select/div/app-address/mat-card/mat-table/mat-row/mat-cell[1]/mat-radio-button')
            address_radio_button.click()
            time.sleep(2)
            # continue with chosen address
            continue_button = self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-select/div/app-address/mat-card/button')
            continue_button.click() 
        except NoSuchElementException:
            print("User " + str(self.user_number) + ": No address set")
            try:
                time.sleep(2)
                self.driver.find_element_by_xpath(
                        '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-select/div/app-address/mat-card/div/button').click()
                time.sleep(0.2)
                self.driver.find_element_by_xpath(
                        '/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[1]/mat-form-field[1]/div/div[1]/div[3]/input').send_keys("Land")
                time.sleep(0.2)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[1]/mat-form-field[2]/div/div[1]/div[3]/input').send_keys("Name")
                time.sleep(0.2)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[1]/mat-form-field[3]/div/div[1]/div[3]/input').send_keys("1234567")
                time.sleep(0.2)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[1]/mat-form-field[4]/div/div[1]/div[3]/input').send_keys("72072")
                time.sleep(0.2)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[1]/mat-form-field[5]/div/div[1]/div[3]/textarea').send_keys("Street")
                time.sleep(0.2)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[1]/mat-form-field[6]/div/div[1]/div[3]/input').send_keys("Stadt")
                time.sleep(0.2)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[1]/mat-form-field[7]/div/div[1]/div[3]/input').send_keys("Bundesland")
                time.sleep(0.2)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-create/div/mat-card/div[2]/button[2]').click()
                time.sleep(2)
                #select address
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-select/div/app-address/mat-card/mat-table/mat-row/mat-cell[1]/mat-radio-button').click()
                time.sleep(2)
                # continue with chosen address
                continue_button = self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-address-select/div/app-address/mat-card/button')
                continue_button.click() 
            except NoSuchElementException:
                print("User " + str(self.user_number) + ": Error adding address")
                return
        try:
            time.sleep(2)
            # choose delivery method
            self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-delivery-method/mat-card/div[3]/mat-table/mat-row[3]/mat-cell[1]/mat-radio-button').click()
            # confirm delivery method
            self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-delivery-method/mat-card/div[4]/button[2]/span').click()
        except NoSuchElementException:
            print("User " + str(self.user_number) + ": Error chosing delivery method")
            return
        try:
            # check if credit card information was added previously
            self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div[1]/mat-table/mat-row/mat-cell[1]/mat-radio-button')
        except NoSuchElementException:
            try: 
                print("User " + str(self.user_number) + ": Add new card information")
                time.sleep(1)
                # add credit card information
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div/mat-expansion-panel/mat-expansion-panel-header').click()
                time.sleep(1)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div/mat-expansion-panel/div/div/div/mat-form-field[1]/div/div[1]/div[3]/input').send_keys('Name')
                time.sleep(1)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div/mat-expansion-panel/div/div/div/mat-form-field[2]/div/div[1]/div[3]/input').send_keys('1234567891011121')
                time.sleep(1)
                month_option = self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div/mat-expansion-panel/div/div/div/mat-form-field[3]/div/div[1]/div[3]/select/option').click()
                time.sleep(1)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div/mat-expansion-panel/div/div/div/mat-form-field[4]/div/div[1]/div[3]/select/option[1]').click()
                time.sleep(1)
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div/mat-expansion-panel/div/div/button').click()
                time.sleep(1)
            except NoSuchElementException:
                print("User " + str(self.user_number) + ": Error choosing credit card information")
                return 
            try:
                time.sleep(1)
                #choose added credit card
                self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/app-payment-method/div/div[1]/mat-table/mat-row/mat-cell[1]/mat-radio-button').click()
                time.sleep(1)
            except NoSuchElementException:
                print("User " + str(self.user_number) + ": Error choosing credit card information")
                return
        try: 
            # continue
            self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-payment/mat-card/div/div[2]/button[2]').click()
            time.sleep(2)
            # checkout
            self.driver.find_element_by_xpath('/html/body/app-root/div/mat-sidenav-container/mat-sidenav-content/app-order-summary/mat-card/div[2]/mat-card/button').click()
            time.sleep(2)
        except NoSuchElementException:
            print("User " + str(self.user_number) + ": error finishing checkout")
        return 1

    def reload(self):
        self.driver.refresh()
            
    def action(self, user_manager):
        """
        register and 
        loop
        --> login user
        --> go shopping(includes leaving feedback) 
        --> complain with uploading zip
        --> logout
        """
        # -->
        if not self.register():
            print("error creating user -> skipping")
            user_manager.remove_user(self)
            return 
        time.sleep(0.1)
        while(self.is_running):
            # -->
            try:
                if not self.login():
                    self.suicide()
            except:
                self.suicide()
            time.sleep(1.5)
            if not self.is_running: 
                self.clean_up_and_quit(user_manager)
                return 
            # -->
            # includes leaving feedback
            self.go_shopping(max_products=10)
            time.sleep(1)
            #-->
            # leave complaint 
            if random.randint(0,10) > 5:
                self.complain()
            # -->
            # checkout cart which was filled in go_shopping()
            if random.randint(0,6) >= 3:
                if self.checkout() == 1:
                    print("User {}: Paid for products".format(self.user_number))
            # logout after shopping
            self.logout()
            # close browser if user was deleted (flag is_running is set)
            if (random.randint(0,10) > 4):
                for i in range(0,10):
                    if not self.is_running:
                        self.clean_up_and_quit(user_manager)
                        return 
                    time.sleep(1)
            if (random.randint(0,3) > 1):
                if not self.is_running:
                    self.clean_up_and_quit(user_manager)
                    return
                time.sleep(5)
                self.driver = webdriver.Chrome(options=self.chrome_options)
        if not self.is_finished:
            self.clean_up_and_quit(user_manager)
    
    def suicide(self):
        """
        stop user actions
        """
        print("Removing User {}".format(self.user_number))
        self.is_running = False
        return self

    def clean_up_and_quit(self, user_manager):
        """
        if user is not supposed to run any more (self.is_running == False)
        set to is_finished and remove user off of remove_users list -> user_manager information
        """
        self.is_finished = True
        print("User {}: was removed".format(self.user_number))
        user_manager.removing_users.remove(self)
        self.driver.quit()
        print("Users in active List: {}".format(len(user_manager.active_users)))
        print("Users in removing List: {}".format(len(user_manager.removing_users)))

        
class UserManager:
    """
    Controlling class of Users
    checking for website availability
    add running users and choose email, password and other needed information
    keep track of running users in active_users
    trigger removing of user -> user.suicide() sets is_running flag of user to false
    keep track of users whos flag was set but jet have to be removed in removing_users
    start sequence of users registering, logging in, starting actions and logging out
    """
    def __init__(self):
        self.active_users = []
        self.sequence_running = False 
        self.removing_users = []
    
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
        print("User {}: was added".format(new_user.user_number))
        try:    
            user_thread = threading.Thread(target=new_user.action, args=([self]))
            user_thread.start()
        except Exception:
            print("Error starting user action")

    def remove_user(self, user = None):
        """
        set is_running Flag to false to stop userActions and end the thread
        remove user from active user list
        add user to removing list until last action is over
        """
        #get last user of list 
        if(len(self.active_users) < 1):
            print("No active users")
            return
        if user:
            print("Remove specific usernumber {}".format(user.user_number))
            user_to_remove = user
        else:
            print("Remove usernumber {}".format(len(self.active_users) - 1))
            user_to_remove = self.active_users[len(self.active_users) - 1]
        self.removing_users.append(user_to_remove)
        self.active_users.remove(user_to_remove)
        test = user_to_remove.suicide()
        print("Users in active List: {}".format(len(self.active_users)))
        print("Users in removing List: {}".format(len(self.removing_users)))
        return user_to_remove

    def remove_all_user(self):
        """
        set is_running flag to false of all users with using suicide function
        """
        #print("Remove usernumber {}".format(len(self.active_users) - 1 - len(self.removing_users)))
        print("Removing all users")
        for i in range(0,len(self.active_users)):
            self.remove_user()

    def start_training_sequence(self):
        """
        automated sequence of adding & removing users
        loop until stop_sequence button is pressed
            add a random number[1:MAX_USERS] of users
            delete random number of users
        """
        print("Training sequence has started")
        self.sequence_running = True
        first_run = True
        while(self.sequence_running):
            print("Users in active List: {}".format(len(self.active_users)))
            print("Users in removing List: {}".format(len(self.removing_users)))
            # add users, but never more than MAX_USERS
            # if first run or no running users add at least one user
            diff_to_MAX_USERS = MAX_USERS - len(self.active_users)
            if first_run or len(self.active_users) == 0:
                users_to_add = random.randint(1,diff_to_MAX_USERS)
                first_run = False
            else:
                users_to_add = random.randint(0,diff_to_MAX_USERS)
            print("Adding {} users.".format(users_to_add))
            for i in range(0,users_to_add):
                self.add_user()
            if not self.sequence_running:
                self.remove_all_user()
                return None
            for i in range(120):
                time.sleep(1)
                if not self.sequence_running:
                    self.remove_all_user()
                    return None
            # remove random number of users 
            random_count = random.randint(0,len(self.active_users))  
            print("Removing {} users".format(random_count))
            print("Users in active List: {}".format(len(self.active_users)))
            print("Users in removing List: {}".format(len(self.removing_users)))
            for j in range(0,random_count):
                self.remove_user()
            if not self.sequence_running:
                self.remove_all_user()
                return None
            print("Users in active List: {}".format(len(self.active_users)))
            print("Users in removing List: {}".format(len(self.removing_users)))
            for i in range(60):
                time.sleep(1)
                if i%10 == 0:
                    print("Waiting {} seconds untill new users are added.".format(60 - i))
                if not self.sequence_running:
                    self.remove_all_user()
                    return None
        self.remove_all_user()
        return None

    def stop_training_sequence(self):
        self.sequence_running = False

if __name__ == "__main__":
    userManager = UserManager()
    userManager.add_user(True)
    time.sleep(100)
    userManager.remove_user()
    time.sleep(200)
