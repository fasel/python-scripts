#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
import subprocess
import fileinput
import random
import time
import sys

import logging
#logging.basicConfig(level=logging.WARN, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(filename='debug_prolific_checker.log', filemode = "w", level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program')

import configparser
config = configparser.ConfigParser(interpolation=None)
config.read('config_prolific_checker.ini')

# constants
MINUTE = 60
URL = "https://app.prolific.co/"
USER_DATA_PATH = config['local']['user_data_path']
USER = config['prolific']['user']
PASS = config['prolific']['pass']

# globals
show_progress = False

# set up browser
options = webdriver.ChromeOptions() 
options.add_argument("user-data-dir=" + USER_DATA_PATH)  #save cookies
#options.add_argument('--disable-blink-features=AutomationControlled')  #stealth
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
#options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36")
# disable crash bubble
options.add_argument("disable-session-crashed-bubble") 
def modify_file_as_text(text_file_path, text_to_search, replacement_text):
    with fileinput.FileInput(text_file_path, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')
modify_file_as_text(USER_DATA_PATH + 'Default/Preferences', 'Crashed', 'none')
    

def printUsage():
    print(f"basic usage: {sys.argv[0]}")
    print(f"show progress bar: {sys.argv[0]} -p")
    print(f"button dump only: {sys.argv[0]} dump")


def getRandInt(min,max):
    return random.randint(min,max)


def notifyUser(topic, text):
    # -t 10000 | timeout in ms (10000=10s)
    # -h string:desktop-entry:org.kde.dolphin | hint with icon (this makes it show up in the notification history)
    subprocess.call(["notify-send", "-t", "10000", "-h", "string:desktop-entry:org.kde.dolphin", "Prolific Checker: " + topic, text])    


def printProgress(status):
    if show_progress == False:
        return
    else:
        print(status, end='', flush=True)


def checkIfLoggedIn():
    logging.debug('Check if logged in.')
    try:
        elemLoginSuccess = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "account-menu-toggle"))
        )
        logging.debug('Successfully logged in. Found element: ' + str(elemLoginSuccess))
        return True
    except:
        logging.warning('Not logged in!')
        return False


def doLogin():
    logging.warning('Logging in.')
    try:
        elemUser = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        elemPass = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        elemButton = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "login"))
        )
        logging.debug('Found elements: ' + str(elemUser) + ' ' + str(elemPass) + ' ' + str(elemButton))

        # log in
        elemUser.send_keys(USER)
        elemPass.send_keys(PASS)
        elemButton.click()

        try:
            # accept cookie
            elemCookie =  WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cm-btn-success"))
            )
            elemCookie.click()
        except Exception as err:
            logging.warning('Cookie message not present.')
            logging.debug('Cookie message err: ' + str(err))
    except Exception as err:
        logging.error('Exception: ' + str(err))
        browser.quit()
        exit("Error: Login elements not found. Exiting.") 


def checkForStudy():
    logging.debug('Checking for study.')
    printProgress(".")
    try:
        wait_time = getRandInt(58,81)
        logging.debug(f'timeout({wait_time})...')

        logging.disable(logging.DEBUG)
        elemTitle =  WebDriverWait(browser, wait_time).until(
            EC.title_contains("(")
        )
        logging.disable(logging.NOTSET)

        logging.debug('Study found!!')
        print("study found!!")

        return True
    except Exception as err:
        logging.disable(logging.NOTSET)
        logging.debug('Element not found (timeout): ' + str(err))
        return False


def checkIfStuck():
    logging.debug('Checking if stuck.')
    try:
        # this element indicates empty study list
        elemOnPage = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "blank-state-title"))
        )

        logging.debug('Page element found. Page is not stuck.')

        return False
    except Exception as err:
        logging.debug('Page element not found. Refresh needed! Infotext: ' + str(err))
        return True


def checkIfStudyPresent():
    logging.debug('Checking if study is present.')
    try:
        '''
        thats the timer span
        <span data-v-0a104dd0="" data-v-c37c6068="" class="text-align-left"> Remaining time you have to complete this study:
<div data-v-1a59804b="" data-v-0a104dd0="" class="timer" data-testid="active-timer" data-v-c37c6068=""><!----><div data-v-1a59804b="" class="timer__counter timer__counter--simple"> 01:02:14 </div></div></span>

        '''
        elemOnPage = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'time you have to complete this study')]"))
        )

        logging.debug('Page element found. Study waiting to be finished!')

        return True
    except Exception as err:
        logging.debug('Page element not found. No study present. Infotext: ' + str(err))
        return False


def screenIsLocked():
    logging.debug('Checking if screen is locked.')
    try:
        cmdout = subprocess.run(["qdbus", "org.kde.screensaver", "/ScreenSaver", "GetActive"], capture_output=True, text=True)
        if cmdout.stdout.strip() == "false":
            logging.debug('Screen is NOT locked.')
            return False
        elif cmdout.stdout.strip() == "true":
            logging.debug('Screen is locked.')
            return True
        else:
            logging.error(f'Error: Screensaver check returned {cmdout.stdout.strip()}. Expected was either true or false. Assuming screen is locked.')
            return True
    except Exception as err:
        logging.error('Something went wrong while checking for screen lock. Quitting. Msg: ' + str(err))
        browser.quit()
        sys.exit(1)

        
def dumpAndExit():
    try:
        notifyUser("Error", "Something went wrong. Exiting. Please have a look.")
        logging.debug(f'Dumping elements.')
        logging.debug(f'Screenshot.')
        browser.save_screenshot('debugscreenie.png')
        ids = browser.find_elements(By.XPATH, '//button')
        logging.debug(f'Dumping elements {len(ids)}:')
        for ii in ids:
            logging.debug(f'role: {ii.aria_role}')
            logging.debug(f'text: {ii.text}')
        browser.quit()
        sys.exit(1)
    except Exception as err:
        logging.error('Something went wrong: ' + str(err))
        browser.quit()
        sys.exit(1)
        

def reservePlace():
    # do not reserve a place when the screen is locked
    if screenIsLocked():
        return

    '''
    card:
    places span element on card:
    <span data-v-e83b940e="" data-testid="study-tag-places"> 877 places </span>
    finder: //span[contains(text(),'place')]

    button #1 to reserve place:
    this is a bit weird. the dump shows a button, but console shows a span.
    so now we try with a span first
    finder: //span[contains(text(),'Take part in this study')]

    button #2
    finder: //button[contains(text(),'Take part in this study')]
    '''
    # find and click first card (optional)
    try:
        elem_card_1 = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'place')]"))
        )
        time.sleep(1.5)  # prevent 'element click intercepted' error
        elem_card_1.click()

    except Exception as err:
        logging.debug('Place reservation: Card not found. Msg: ' + str(err))

    # find and click reserve place button #1
    try:
        elem_reserve_button = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'ake part in this study')]"))
        )
        browser.execute_script("arguments[0].scrollIntoView();", elem_reserve_button);
        elem_reserve_button.click()

        print("Place reserved (button1). Start the study!")
        notifyUser("Place reserved", "Switch to a browser and start the study!")

    except Exception as err: 
        logging.debug('Place reservation: Button 1 not found. Msg: ' + str(err))
        logging.debug('trying button 2')

        # find and click reserve place button #2
        try:
            elem_reserve_button2 = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'ake part in this study')]"))
            )
            elem_reserve_button2.click()

            print("Place reserved (button2). Start the study!")
            notifyUser("Place reserved", "Switch to a browser and start the study!")

        except Exception as err: 
            logging.debug('Place reservation: Button 2 not found. Msg: ' + str(err))
            logging.debug('giving up.')
            dumpAndExit()


# process command line options
if len(sys.argv) > 1:
    if sys.argv[1] == "dump":
        browser = webdriver.Chrome(options=options)
        browser.get(URL)
        time.sleep(8)
        dumpAndExit()
    if sys.argv[1] == "-p":
        show_progress = True
    else:
        printUsage()
        exit(1)

# MAIN
try:
    browser = webdriver.Chrome(options=options)
    browser.get(URL)
    error_check = 0
    while error_check <= 3:
        printProgress("\r")
        printProgress(f'_{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}_: ')
        printProgress(f"e({error_check})")
        if checkIfLoggedIn():
            printProgress(".")
            if checkForStudy():  # waits ~60 seconds
                printProgress("!")
                reservePlace()  # waits ~5-15 seconds
                # problem: study might be full. button remains there.
                # solution: refresh, just in case

            if checkIfStudyPresent():
                printProgress(".")
                # sleeping for a while
                # you lose the slot after 10 minutes if you dont start the study
                # but we wait less because it might have been finished in the meantime
                sleep_time = 5 * MINUTE  
                logging.debug(f'sleeping({sleep_time})...')
                time.sleep(sleep_time)

            if checkIfStuck():
                printProgress("s")
                # do a refresh, just in case
                # prolific autoupdate tends to get stuck
                # directly loading study page instead of just doing refresh
                # because we might be stuck in a full or time outed study
                logging.warning('Refreshing Page.')
                browser.get(URL + 'studies')
        else:
            printProgress("w")
            doLogin()
            error_check += 1
        # sleep to prevent hammering
        # randomize for stealth
        sleep_time = getRandInt(11,17)
        logging.debug(f'sleeping({sleep_time})...')
        time.sleep(sleep_time)
    logging.error('Too many retries. (' + str(error_check) + '). Exiting.')
    browser.quit()
    exit(1)
except KeyboardInterrupt as err:
    logging.error('Keyboard interrupted. (' + str(err) + '). Exiting.')
    browser.quit()
    sys.exit(1)


