#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('/usr/local/lib/python2.7/site-package')
sys.path.append('/home/ec2-user/workspace/work')

import requests
from requests_oauthlib import OAuth1Session
#from pprint import pprint
from consts import *
import json
import os
import datetime
# Imports the Google Cloud client library
from google.cloud import translate

from twitterAPIManager import TwitterAPIManager
manager = TwitterAPIManager()

import pytz
JST = pytz.timezone('Asia/Tokyo')

WORK_FILE_PATH = '/home/ec2-user/workspace/work/'

# タイムライン取得用のURL
url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
# 翻訳API用URL
transUrl = "curl https://hogefuga.execute-api.ap-northeast-1.amazonaws.com/test/translate?text={0}"


def main():
    for key in qryptors:
        screenName = qryptors[key]["screen_name"]
        webhookUrl = qryptors[key]["webhook"]
        needTranslation = qryptors[key]["need_translation"]
        print (webhookUrl)
        sinceId = readSinceTweetId(screenName)
        if sinceId and sinceId != "0":
            params = {'screen_name': screenName, 'since_id': sinceId, 'count': 10, 'tweet_mode': 'extended', 'exclude_replies': 'true', 'include_rts': 'false'}
        else:
            params = {'screen_name': screenName, 'count': 1, 'tweet_mode': 'extended', 'exclude_replies': 'true', 'include_rts': 'false'}
        
        # OAuth で GET
        key = manager.nextKey()
        twitter = OAuth1Session(key.consumerKey, key.consumerSecret, key.accessToken, key.accessTokenSecret)
        req = twitter.get(url, params = params)
        
        if req.status_code == 200:
            # レスポンスはJSON形式なので parse する
            timeline = json.loads(req.text)
            # 各ツイートの本文を表示
            newId = "0"

            for tweet in timeline:
                if newId == "0":
                    newId = str(tweet["id"])
                bodyText = tweet["full_text"]
                if needTranslation:
                    translated = translateByAPI(bodyText)
                    postToDiscord(webhookUrl, tweet["id"], screenName, bodyText, translated, tweet["user"]["profile_image_url"], tweet["created_at"], needTranslation)
                else:
                    postToDiscord(webhookUrl, tweet["id"], screenName, bodyText, "", tweet["user"]["profile_image_url"], tweet["created_at"], needTranslation)

            print(newId)
            if len(timeline) > 0:
                writeSinceTweetId(screenName, newId)

        else:
            # エラーの場合
            print ("Error: %d" % req.status_code)
            
def translateByAPI(text):
    # Instantiates a client
    translate_client = translate.Client()
    
    # The text to translate
    # The target language
    target = 'ja'    
    translation = translate_client.translate(
        text,
        target_language=target)
    
    print(u'Text: {}'.format(text))
    print(u'Translation: {}'.format(translation['translatedText']))
    
    return translation['translatedText']

    
def readSinceTweetId(screenName):
    filePath = WORK_FILE_PATH + getIdFileName(screenName)
    if not os.path.exists(filePath):
        return "0"
    file = open(filePath, 'r')  #ファイルをオープン
    id = file.read()
    file.close()              #ファイルをクローズ
    return id
    
def writeSinceTweetId(screenName, id):
    filePath = WORK_FILE_PATH + getIdFileName(screenName)
    file = open(filePath, 'w')  #ファイルをオープン
    print ("write:" + id)
    file.write(id)
    file.close()              #ファイルをクローズ
    
def getIdFileName(screenName):
    return screenName + "_sinceid.txt"
    
def asLocalize(createdAt):
    return datetime.datetime.strptime(createdAt, "%a %b %d %H:%M:%S %z %Y").astimezone(JST).strftime('%Y/%m/%d %H:%M:%S')

def postToDiscord(url, id, screenName, text, translated, profileImageUrl, createdAt, needTranslation):
    param = json.dumps(getJsonTemplate(id, screenName, text, translated, profileImageUrl, createdAt, needTranslation))

    response = requests.post(
    url,
    param,
    headers={'Content-Type': 'application/json'})

def getJsonTemplate(id, screenName, text, translated, profileImageUrl, createdAt, needTranslation):
    if needTranslation:
        return {
            "attachments": [
                {
                    "color": "#36a64f",
                    "author_name": "@" + screenName,
                    "author_link": "https://twitter.com/{screenName}/status/{id}".format(screenName=screenName, id=id),
                    "author_icon": profileImageUrl,
                    "fields": [
                        {
                            "value": text,
                            "short": "false"
                        },
        				{
        					"title": "翻訳結果",
        					"value": translated,
        					"short": "false"
        				}
                    ],
                    "footer": asLocalize(createdAt)
                }
            ]
        }
    else:
        return {
            "attachments": [
                {
                    "color": "#36a64f",
                    "author_name": "@" + screenName,
                    "author_link": "https://twitter.com/{screenName}/status/{id}".format(screenName=screenName, id=id),
                    "author_icon": profileImageUrl,
                    "fields": [
                        {
                            "value": text,
                            "short": "false"
                        }
                    ],
                    "footer": asLocalize(createdAt)
                }
            ]
        }

if __name__== '__main__':
    main()

