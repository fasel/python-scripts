#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re

import sys

import logging
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.WARN, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program')


# constants
#URL = "https://www.httpbin.org/headers"
URL_SEARCH_STRING = 'https://www.youtube.com/watch?v='


# set up browser
options = webdriver.ChromeOptions() 
options.add_argument("--headless");
options.add_argument('window-size=1080x1920');
browser = webdriver.Chrome(options=options)


def printUsage():
    print(f"usage: {sys.argv[0]} <YOUTUBE_URL>")
    print(f"YOUTUBE_URL is a direct link to a YouTube video")


def getVideoStats(URL):
    try:
        logging.debug('Loading: ' + URL)
        browser.get(URL)

        # view count
        elem_view_count = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'view-count'))
        )

        # likes
        elem_likes = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[6]/div[2]/ytd-video-primary-info-renderer/div/div/div[3]/div/ytd-menu-renderer/div[1]/ytd-toggle-button-renderer[1]/a/yt-formatted-string'))
        )

        # comments
        elem_comments = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]'))
        )

        # title
        elem_title = browser.title

        # counts
        view_count = re.sub('[,.a-zA-Z ]', '', elem_view_count.text)
        view_count = int(view_count)
        likes = int(elem_likes.text)
        comments = int(elem_comments.text)

        ratio_view_like = view_count / likes
        ratio_view_comment = view_count / comments
        ratio_comment_like = likes / comments

        # TODO: judge the ratios
        # towards 1 is better
        ''' some results:
ABSOLUTH x KEIN BOCK ORIGINALS | Kanal abonnieren! - YouTube
view count: 1599 _ likes: 24 _ comments: 3
view to like ratio: 66.62
view to comment ratio: 533.00
comment to like ratio: 8.00

Lúcia Lu | HÖR - Apr 12 / 2022 - YouTube
view count: 25834 _ likes: 1405 _ comments: 121
view to like ratio: 18.39
view to comment ratio: 213.50
comment to like ratio: 11.61

Lost Control w/ Black Eyes | HÖR - Apr 14 / 2022 - YouTube
view count: 2071 _ likes: 77 _ comments: 4
view to like ratio: 26.90
view to comment ratio: 517.75
comment to like ratio: 19.25

Bash Back 2022 - YouTube
view count: 98 _ likes: 20 _ comments: 4
view to like ratio: 4.90
view to comment ratio: 24.50
comment to like ratio: 5.00


        '''

        # Printout
        print(elem_title)
        print(f'view count: {view_count} _ likes: {likes} _ comments: {comments}')
        print(f'view to like ratio: {ratio_view_like:.2f}')
        print(f'view to comment ratio: {ratio_view_comment:.2f}')
        print(f'comment to like ratio: {ratio_comment_like:.2f}')

        browser.quit()
    except Exception as err:
        logging.error('Page load failed: ' + str(err))
        browser.quit()
        exit(1)

# process command line options
if len(sys.argv) > 1:
    if URL_SEARCH_STRING in sys.argv[1]:
        logging.debug("Printing video stats:")
        getVideoStats(sys.argv[1])
        logging.debug("Bye.")
    elif sys.argv[1] == "--help":
        printUsage()
        exit()
    else:
        print("Error: invalid option.")
        printUsage()
        exit(1)
else:
    print("Error: Missing option.")
    printUsage()
    exit(1)

