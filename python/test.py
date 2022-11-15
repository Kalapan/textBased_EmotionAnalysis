from datetime import datetime, date
from http import client
from dotenv import dotenv_values, load_dotenv
import tweepy
import sys


#show which env file the credentials are stored in
config = dotenv_values(".env")

#authenticate twitter account using credentials from the env file
authenticate = tweepy.OAuthHandler(config["api_key"], config["api_key_secret"])
authenticate.set_access_token(config["access_token"], config["access_token_secret"])
api = tweepy.API(authenticate)

username = 'elonMusk'

tmpTweets = tweets = api.user_timeline(screen_name = username, count = 200, include_rts = False, tweet_mode = 'extended')

for info in tweets [:500]:

    print(info.created_at)

