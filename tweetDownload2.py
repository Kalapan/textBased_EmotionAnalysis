from http import client
from dotenv import dotenv_values, load_dotenv
import snscrape.modules.twitter as sntwitter
import pandas as pd
from pymongo import MongoClient
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline
import sys

#show which env file the credentials are stored in
config = dotenv_values(".env")
#connect to the mongodb database
client = MongoClient(config["MongoLogIn"])
#get database
db = client.get_database('User')
#get collection object in database
tweets_collection = db.tweets_information

#required to make the text analyzer know where to get required model and architecture
tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")
#assign which model to use
emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')

#assign the users twitter id to userID
userID = str(sys.argv[1])
autoMonthStart = str(sys.argv[2])
autoMonthInt = int(sys.argv[2]) + 1
autoMonthEnd = str(autoMonthInt)

def pullAnalyzeTweet(startDate, endDate):
    fromTag = "from:"
    startD = "since:" + startDate
    endD = "until:" + endDate
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
        #get the emotion of the tweet
        emotion_labels = emotion(tweet.content)
        #convert the list to a dictionary
        emotionOutput = emotion_labels[0]
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

        # check if the tweet already exists in database
        item_details = tweets_collection.find_one({
            "Tweet": tweet,
        })
        # if tweet does not exist in database
        if item_details is None:
            # add all the data to an array
            data.append([userID, tweetDate, tweetMonth, tweetYear, tweetTime, tweet, emotionType, emotionScore])
            dataExists = 1
            print("Data inserted into the database.")
        else:
            print("Data already exists in the database.")
            break

    # convert data into a dataframe
    df = pd.DataFrame(data, columns = columns)
    # make the dataframe a dictionary
    data = df.to_dict(orient = "records")
    if dataExists == 1:
        # send the dictionary to mongodb
        tweets_collection.insert_many(data)

if autoMonthInt != 13:
    pullAnalyzeTweet("2023-" + autoMonthStart + "-01", "2023-" + autoMonthEnd + "-01")
else:
    pullAnalyzeTweet("2023-12-01", "2023-12-31")

if autoMonthInt != 13:
    pullAnalyzeTweet("2022-" + autoMonthStart + "-01", "2022-" + autoMonthEnd + "-01")
else:
    pullAnalyzeTweet("2022-12-01", "2022-12-31")