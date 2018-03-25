#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from requests_oauthlib import OAuth1Session
#from pprint import pprint
# from consts import *
import json
import os
import datetime
import re
from time import sleep

import pytz
JST = pytz.timezone('Asia/Tokyo')
WORK_FILE_PATH = '/home/ec2-user/workspace/work/'

# TwitterAPIKey
# 本来は環境変数に格納しておくが、運用上の利便性の為直接記述
CK = 'HOGEHOGE'                             # Consumer Key
CS = 'FUGAFUGA'         # Consumer Secret
AT = '000000000-HOGEFUGA' # Access Token
AS = 'FUGAHOGE'         # Accesss Token Secret

# 上場銘柄取得先、フィルタリングパターン、Webhook投稿先(Discord)
tradingServices = {
    "Binance":{"screen_name":"binance", "pattern":r"#?binance lists ", "webhook":"https://discordapp.com/api/webhooks/000000000000000000/hogefuga/slack"}
}

# タイムライン取得用のURL
url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
# 翻訳APIURL
transUrl = "curl https://hogefuga.execute-api.ap-northeast-1.amazonaws.com/test/translate?text={0}"


def main():
    for key in tradingServices:
        screenName = tradingServices[key]["screen_name"]
        webhookUrl = tradingServices[key]["webhook"]
        pattern = tradingServices[key]["pattern"]

        sinceId = readSinceTweetId(screenName)
        shouldToPost = sinceId and sinceId != "0" # 初回はDiscordに投稿しない
        if shouldToPost:
            params = {'screen_name': screenName, 'since_id': sinceId, 'count': 10, 'tweet_mode': 'extended', 'exclude_replies': 'true', 'include_rts': 'false'}
        else:
            params = {'screen_name': screenName, 'count': 1, 'tweet_mode': 'extended', 'exclude_replies': 'true', 'include_rts': 'false'}

        # OAuth で GET
        twitter = OAuth1Session(CK, CS, AT, AS)
        req = twitter.get(url, params = params)
        
        if req.status_code == 200:
            # レスポンスはJSON形式なので parse する
            timeline = json.loads(req.text)
            # pprint(timeline)
            # 各ツイートの本文を表示
            newId = "0"
            # フィルタリング条件
            repatter = re.compile(pattern)

            for tweet in timeline:
                if newId == "0":
                    newId = str(tweet["id"])
                bodyText = tweet["full_text"]

                # List情報のみ投稿
                matchOB = repatter.match(bodyText.lower())
                if matchOB and shouldToPost:
                    postToDiscord(webhookUrl, tweet["id"], screenName, bodyText, "", tweet["user"]["profile_image_url"], tweet["created_at"], False)
                    sleep(5)

            if len(timeline) > 0:
                writeSinceTweetId(screenName, newId)

        else:
            # エラーの場合
            print ("Error: %d" % req.status_code)
            
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
    file.write(id)
    file.close()              #ファイルをクローズ
    
def getIdFileName(screenName):
    return "{name}_sinceid_for_pickup_listed.txt".format(name=screenName)
    
def asLocalize(createdAt):
    return datetime.datetime.strptime(createdAt, "%a %b %d %H:%M:%S %z %Y").astimezone(JST).strftime('%Y/%m/%d %H:%M:%S')

def postToDiscord(url, id, screenName, text, translated, profileImageUrl, createdAt, needTranslation):
    mentionParam = json.dumps(getMentionTemplate())
    param = json.dumps(getJsonTemplate(id, screenName, text, translated, profileImageUrl, createdAt, needTranslation))
    # print (param)
    response = requests.post(
    url[0:-6], # /slack部分を取り除く
    mentionParam,
    headers={'Content-Type': 'application/json'})

    response = requests.post(
    url,
    param,
    headers={'Content-Type': 'application/json'})

def getJsonTemplate(id, screenName, text, translated, profileImageUrl, createdAt, needTranslation):
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

def getMentionTemplate():
    return {
        "content" : "@everyone"
    }

if __name__== '__main__':
    main()

