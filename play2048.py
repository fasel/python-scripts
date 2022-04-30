#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import random
import time

browser = webdriver.Chrome()
browser.get('https://play2048.co/')

# accept cookie
linkElem = browser.find_element(By.ID,"ez-accept-all")
linkElem.click()

def get_keypress(randomInt):
    if randomKey == 1:
        return Keys.LEFT
    elif randomKey == 2:
        return Keys.RIGHT
    elif randomKey == 3:
        return Keys.DOWN
    elif randomKey == 4:
        return Keys.UP

while True:
    randomKey = random.randint(1,4)
    browserKey = get_keypress(randomKey)
    htmlElem = browser.find_element(By.TAG_NAME,"html")
    htmlElem.send_keys(browserKey)
    time.sleep(1)
    print(f'{randomKey} .')

