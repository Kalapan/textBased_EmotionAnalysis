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

#assign the users twitter id to userID
# userID = str(sys.argv[1])
userID = 'elonMusk'
fromTag = "from:"
endDate = "until:2022-05-01"
startDate = "since:2022-04-01"
query = fromTag + userID + " " + startDate + " " + endDate

#set the column title which the tweets will be saved in
columns = ['Twitter_ID','Date', 'Month', 'Time', 'Tweet', 'Emotion', 'Value']
#make an array to hold the data
data = []

# Using TwitterSearchScraper to scrape data and append tweets to list
for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
    if i>20:
        break
    #assign which model to use
    emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')
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
    # get the tweet time
    tweetTime = tweet.date.strftime("%H:%M:%S")

    # add all the data to an array
    data.append([userID, tweetDate, tweetMonth, tweetTime, tweet.content, emotionType, emotionScore])

# convert data into a dataframe
df = pd.DataFrame(data, columns = columns)

# make the dataframe a dictionary
data = df.to_dict(orient = "records")

# send the dictionary to mongodb
tweets_collection.insert_many(data)