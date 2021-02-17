#Importing Libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
import time
from datetime import datetime, timedelta
from datetime import date
import schedule
from webdriver_manager.chrome import ChromeDriverManager 
import discord_webhook 
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('keys.env')



opt = Options()

opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--disable-infobars")
opt.add_argument("--headless")


driver = None




load_dotenv(dotenv_path=dotenv_path)

user = os.getenv('USER_ID')
password = os.getenv('PASSWORD')
URL = os.getenv('URL')




def login(portal):

    global driver
    count = 0

    #Logging in
    print("logging in")
    user_id = driver.find_element_by_id("txtusername")
    user_id.send_keys(user)
    paswd = driver.find_element_by_id("password")
    paswd.send_keys(password)
    
    time.sleep(1)
    driver.find_element_by_id("Submit").click()
    


    # Enter into G-learn 
    

    timetable_btn = None
    while True:
        try:
            if portal == 'glearn':
                if ("https://login.gitam.edu/studentapps.aspx" in driver.current_url):
                    glearn_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "G-Learn")))
                    glearn_btn.click()
                    
                class_table = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@id='ContentPlaceHolder1_divlblonline']")))
                class_table.location_once_scrolled_into_view
                # Maybe not required
                if not(type(class_table) == type(None)):
                    break

            if portal == 'student_timetable':
                if ("https://login.gitam.edu/studentapps.aspx" in driver.current_url):
                    glearn_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "G-Learn")))
                    glearn_btn.click()

                timetable_btn = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.LINK_TEXT, "My timetable")))
                timetable_btn.location_once_scrolled_into_view

                if not(type(timetable_btn) == type(None)):
                    timetable_btn.click()
                    break

        except:
            if count>15:
                print('Looks like G-learn is down') 

                # G-learn down send msg to discord
                discord_webhook.send_msg(class_name='-',link='-',status="G-learn down",date='-',start_time='-',end_time='-')
                return
            time.sleep(15)
            print("trying again")
            count = count+1
            driver.refresh()
    
    print('Logged in')
    time.sleep(5)   








# Extracting time
def extract_time(date_time):
    str = date_time
    time = str.split()
    tmp = time[4].split(':')
    tmp2 = []
    tmp2 = tmp[1] +":"+ tmp[2]
    return tmp2



# CONVERSION 12hr to 24hr
def convert_time(timing):
    in_time = datetime.strptime(timing, "%I:%M%p")
    out_time = datetime.strftime(in_time, "%H:%M")
    return out_time








def fetch_link(class_name,start_time,end_time):
    global driver
    
    #time.sleep(10)
    #driver.refresh()
    #time.sleep(10)

    try:
        driver.refresh()
        time.sleep(10)
        glearn_url = 'http://glearn.gitam.edu/student/welcome.aspx'
        if not((glearn_url).lower() == (driver.current_url).lower()):
            print('glearn not loaded')
            login('glearn')



    except:
        driver.close()
        time.sleep(10)
        print('Browser closed, opening again')
        start_browser()

    
    today_date = date.today() # Today's date
    count = 0
    check = False

    while True:
        
        # List is created
        classes_available = driver.find_elements_by_xpath("//table[@id='ContentPlaceHolder1_GridViewonline']/tbody/tr") 

        for i in range(len(classes_available)):

            # Class name
            x_path1 = f"//*[@id='ContentPlaceHolder1_GridViewonline']/tbody/tr[{i+1}]/td/a/div/h4" 

            # date and time 
            x_path2 = f"//table[@id='ContentPlaceHolder1_GridViewonline']/tbody/tr[{i+1}]/td/a/div/h6" 

            className = driver.find_element_by_xpath(x_path1).text
            date_time = driver.find_element_by_xpath(x_path2).text

            # Extract Time
            timing = extract_time(date_time) 
            converted_time = convert_time(timing)
            
            # Extract Day
            temp = date_time.split()
            class_date = (temp[2].split("-"))[0]
            class_date = int(class_date)

            # Extract Date
            dat = date_time.split(':')
            dat = dat[1]




            if start_time == converted_time and today_date.day == class_date:

                check = True

                link = f"//tbody/tr[{i+1}]/td[1]/a" 

                zoom_link = driver.find_element_by_xpath(link).get_attribute('href')
                time.sleep(5)

                # Send Link to Discord
                discord_webhook.send_msg(class_name=className,status="fetched",link=zoom_link,date=dat,start_time=start_time,end_time=end_time)
                break


        if check == False:

            if count>15:
                print("No class")

                # NO class send msg to discord
                discord_webhook.send_msg(class_name=class_name,link='-',status="noclass",date=dat,start_time=start_time,end_time=end_time)
                return

            print("Class not found, trying again")
            time.sleep(60)
            driver.refresh()
            count +=1
            time.sleep(3)

        if check == True:
            break 
    

    time.sleep(5)





def sched():

    # Start browser
    print('browser started')
    global driver
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=opt,service_log_path='NUL')
    driver.get(URL)
    WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

    login('student_timetable')

    # Schedule all classes
    timetable = driver.find_elements_by_xpath("//table[@id='ContentPlaceHolder1_grd1']/tbody/tr") 
    columns = timetable[0].find_elements_by_tag_name('th')

    for i in range(len(timetable)+1):


        for j in range(2,len(columns)):

            if i>1:

                class_name_xpath = f"//table[@id='ContentPlaceHolder1_grd1']/tbody/tr[{i}]/td[{j}]"
                class_name = driver.find_element_by_xpath(class_name_xpath).text
                if not class_name == "":

                    
                    day_xpath = f"//table[@id='ContentPlaceHolder1_grd1']/tbody/tr[{i}]/td[{1}]"
                    day = driver.find_element_by_xpath(day_xpath).text

                    timings_xpath = f"//table[@id='ContentPlaceHolder1_grd1']/tbody/tr[{1}]/th[{j}]"
                    timings = driver.find_element_by_xpath(timings_xpath).text
                    timings_split = timings.split('to')
                    start_time = timings_split[0].strip()
                    end_time = timings_split[1].strip()


                    # To get the message 10 minutes before the class
                    tmp = "%H:%M"
                    msg_tmp = datetime.strptime(start_time,tmp)
                    ten_minutes = timedelta(minutes=10)
                    msg_time = msg_tmp - ten_minutes
                    msg_time = datetime.strftime(msg_time,tmp)


                    if day.lower()=="monday":
                        schedule.every().monday.at(msg_time).do(fetch_link,class_name,start_time,end_time)
                        print(f"Scheduled class {class_name} on {day} at {start_time}")
                    if day.lower()=="tuesday":
                        schedule.every().tuesday.at(msg_time).do(fetch_link,class_name,start_time,end_time)
                        print(f"Scheduled class {class_name} on {day} at {start_time}")
                    if day.lower()=="wednesday":
                        schedule.every().wednesday.at(msg_time).do(fetch_link,class_name,start_time,end_time)
                        print(f"Scheduled class {class_name} on {day} at {start_time}")
                    if day.lower()=="thursday":
                        schedule.every().thursday.at(msg_time).do(fetch_link,class_name,start_time,end_time)
                        print(f"Scheduled class {class_name} on {day} at {start_time}")
                    if day.lower()=="friday":
                        schedule.every().friday.at(msg_time).do(fetch_link,class_name,start_time,end_time)
                        print(f"Scheduled class {class_name} on {day} at {start_time}")
                    if day.lower()=="saturday":
                        schedule.every().saturday.at(msg_time).do(fetch_link,class_name,start_time,end_time)
                        print(f"Scheduled class {class_name} on {day} at {start_time}")
                    if day.lower()=="sunday":
                        schedule.every().sunday.at(msg_time).do(fetch_link,class_name,start_time,end_time)
                        print(f"Scheduled class {class_name} on {day} at {start_time}")



                else:
                    continue


    print('All Classes are Scheduled')


    count = 0
    while True:

        try:
            back_btn = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH,"//div[@class='col-md-12']//img[1]")))
            back_btn.click()
            class_table = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@id='ContentPlaceHolder1_divlblonline']")))
            class_table.location_once_scrolled_into_view
            if not(type(class_table) == type(None)):
                break

        except:
            if count>15:
                print('Looks like G-learn is down') 

                # G-learn down send msg to discord
                discord_webhook.send_msg(class_name='-',link='-',status="G-learn down",date='-',start_time='-',end_time='-')
                break
            time.sleep(15)
            print("trying again")
            count = count+1
            driver.refresh()





    while True:
        # Checks whether a scheduled task is pending to run or not
        schedule.run_pending()
        time.sleep(1)





def start_browser():

    print('Browser started')

    global driver
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=opt,service_log_path='NUL')

    driver.get(URL)

    WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

    login('glearn')






if __name__=="__main__":
   
    while True:
        op = int(input(("\n1. Start Bot\n2. Exit\n\nEnter option : ")))
    
        if(op==1):
            sched()
           
        if(op==2):
            exit()