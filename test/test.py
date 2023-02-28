# import requests

# API_URL = "https://api-inference.huggingface.co/models/arpanghoshal/EmoRoBERTa"
# headers = {"Authorization": "Bearer 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"}

# def query(payload):
# 	response = requests.post(API_URL, headers = headers, json = payload)
# 	return response.json()
	
# output = query({
# 	"inputs": "i love you",
# })
# print(output[0][0])
from http import client
from dotenv import dotenv_values, load_dotenv
import snscrape.modules.twitter as sntwitter
import pandas as pd
from pymongo import MongoClient
import sys
import requests

API_URL = "https://api-inference.huggingface.co/models/arpanghoshal/EmoRoBERTa"
headers = {"Authorization": "Bearer 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"}

#show which env file the credentials are stored in
config = dotenv_values(".env")
#connect to the mongodb database
client = MongoClient(config["MongoLogIn"])
#get database
db = client.get_database('User')
#get collection object in database
tweets_collection = db.tweets_information

def query2(payload):
    response = requests.post(API_URL, headers = headers, json = payload)
    return response.json()

#assign the users twitter id to userID
userID = 'elonMusk'

fromTag = "from:"
startD = "since:" + "2023-01-01"
endD = "until:" + "2023-01-31"
query = fromTag + userID + " " + startD + " " + endD
dataExists = 0
#set the column title which the tweets will be saved in
columns = ['Twitter_ID','Date', 'Month', 'Year', 'Time', 'Tweet', 'Emotion', 'Value']
#make an array to hold the data
data = []
# Using TwitterSearchScraper to scrape data and append tweets to list
for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
	if i>10:
		break
	outputTweet = query2({
		"inputs": tweet.content,
	})
	emotion_labels = outputTweet[0][0]
	#convert the list to a dictionary
	emotionOutput = emotion_labels
	#get the emotion type and assign to a variable
	emotionType = emotionOutput.get('label')
	#get the emotion value and round to 2 decimal places
	emotionScore = round(emotionOutput.get('score'), 2)
	# get the tweet date
	tweetDate = tweet.date.strftime("%m-%d-%Y")
	# get the tweet month
	tweetMonth = tweet.date.strftime("%m")
	tweetYear = tweet.date.strftime("%Y")
	# get the tweet time
	tweetTime = tweet.date.strftime("%H:%M:%S")
	#remove line break
	tweet = tweet.content.replace("\n", "").replace("'", "").replace('"', '')

	data.append([userID, tweetDate, tweetMonth, tweetYear, tweetTime, tweet, emotionType, emotionScore])
	# if tweet does not exist in database
# convert data into a dataframe
df = pd.DataFrame(data, columns = columns)
print(df)
# make the dataframe a dictionary
data = df.to_dict(orient = "records")
# tweets_collection.insert_many(data)
