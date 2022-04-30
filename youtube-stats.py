#!/usr/bin/env python3

import os
import re
import sys
import pprint
import subprocess

from colorama import Fore, Style

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import logging
#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.WARN, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program')

import configparser
config = configparser.ConfigParser()
config.read('config_youtube-stats.ini')

# constants
DEVKEY = config['google-api']['developer_key']
URL_SEARCH_STRING = 'https://www.youtube.com/watch?v='


def printUsage():
    print(f"usage: {sys.argv[0]} <YOUTUBE_URL>")
    print(f"YOUTUBE_URL is a direct link to a YouTube video")


def getVideoID(URL):
    return re.sub(r'&.*$', '', re.sub(re.escape(URL_SEARCH_STRING), '', URL))


def getClipboard():
    cmdout = subprocess.run(["xsel", "--clipboard"], capture_output=True, text=True)
    return cmdout.stdout.strip()


def getVideoStats(URL):
        # YouTube setup
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"

        youtube = googleapiclient.discovery.build(
            api_service_name, 
            api_version, 
            developerKey=DEVKEY #generate in https://console.cloud.google.com/apis/credentials
        )

        request = youtube.videos().list(
            part="snippet,statistics",
            id=getVideoID(URL)
        )
        response = request.execute()
        #pprint.pprint(response)

        # title
        elem_title = response['items'][0]['snippet']['title']

        # counts
        view_count = int(response['items'][0]['statistics']['viewCount'])
        likes = int(response['items'][0]['statistics']['likeCount'])
        comments = int(response['items'][0]['statistics']['commentCount'])

        # calculate ratios
        # prevent division by zero
        ratio_view_like = likes and view_count / likes or 0
        ratio_view_comment = comments and view_count / comments or 0
        ratio_comment_like = comments and likes / comments or 0

        # Printout
        # judgement: towards 1 is better. marked with red/green star depending on threshold
        # TODO: is video controversial? (maybe comment-ratio to like-ratio)
        print(elem_title)
        print(f'view count: {view_count} _ likes: {likes} _ comments: {comments}')

        print(f'view to like ratio: {round(ratio_view_like, 2)}', end='')
        if ratio_view_like > 30:
            print(f"{Fore.RED}*{Style.RESET_ALL}")
        elif 20 > ratio_view_like > 0:
            print(f"{Fore.GREEN}*{Style.RESET_ALL}")
        else:
            print("")

        print(f'view to comment ratio: {round(ratio_view_comment, 2):}', end='')
        if ratio_view_comment > 600:
            print(f"{Fore.RED}*{Style.RESET_ALL}")
        elif 300 > ratio_view_comment > 0:
            print(f"{Fore.GREEN}*{Style.RESET_ALL}")
        else:
            print("")

        print(f'comment to like ratio: {round(ratio_comment_like, 2):}', end='')
        if ratio_comment_like > 50:
            print(f"{Fore.RED}*{Style.RESET_ALL}")
        elif 20 > ratio_comment_like > 0:
            print(f"{Fore.GREEN}*{Style.RESET_ALL}")
        else:
            print("")

# process command line options
if len(sys.argv) > 1:
    if URL_SEARCH_STRING in sys.argv[1]:
        logging.debug("Printing video stats:")
        getVideoStats(sys.argv[1])
    elif sys.argv[1] == "--help":
        printUsage()
        exit()
    elif sys.argv[1] == "magic":
        clip = getClipboard()
        if URL_SEARCH_STRING in clip:
            logging.debug("Printing video stats:")
            getVideoStats(clip)
    else:
        print("Error: invalid option.")
        printUsage()
        exit(1)
else:
    print("Error: Missing option.")
    printUsage()
    exit(1)


