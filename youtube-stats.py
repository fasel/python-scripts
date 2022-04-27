#!/usr/bin/env python3

import os
import sys
import re
import pprint

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


def getVideoID():
    return sys.argv[1].replace(URL_SEARCH_STRING, '')


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
            id=getVideoID()
        )
        response = request.execute()
        #pprint.pprint(response)

        # title
        elem_title = response['items'][0]['snippet']['title']

        ## counts
        view_count = int(response['items'][0]['statistics']['viewCount'])
        likes = int(response['items'][0]['statistics']['likeCount'])
        comments = int(response['items'][0]['statistics']['commentCount'])

        ratio_view_like = view_count / likes
        ratio_view_comment = view_count / comments
        ratio_comment_like = likes / comments

        # Printout
        # TODO: judge the ratios - towards 1 is better
        # TODO: is video controversial? (maybe comment-ratio to like-ratio)
        print(elem_title)
        print(f'view count: {view_count} _ likes: {likes} _ comments: {comments}')
        print(f'view to like ratio: {ratio_view_like:.2f}')
        print(f'view to comment ratio: {ratio_view_comment:.2f}')
        print(f'comment to like ratio: {ratio_comment_like:.2f}')

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


