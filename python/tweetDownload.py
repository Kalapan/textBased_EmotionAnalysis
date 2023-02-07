from http import client
from dotenv import dotenv_values, load_dotenv
import tweepy
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

#authenticate twitter account using credentials from the env file
authenticate = tweepy.OAuthHandler(config["api_key"], config["api_key_secret"])
authenticate.set_access_token(config["access_token"], config["access_token_secret"])
api = tweepy.API(authenticate)

#required to make the text analyzer know where to get required model and architecture
tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")

#assign the users twitter id to userID
userID = str(sys.argv[1])
# userID = 'elonMusk'

#parameters set to get the tweets
tweets = api.user_timeline(screen_name = userID, count = 200, include_rts = False, exclude_replies = True, tweet_mode = 'extended')

#set the column title which the tweets will be saved in
columns = ['Twitter_ID','Date', 'Time', 'Tweet', 'Emotion', 'Value']
#make an array to hold the data
data = []

#get the latest tweet and format
for info in tweets [:5]:
    #assign which model to use
    emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')
    #get the emotion of the tweet
    emotion_labels = emotion(info.full_text)
    #convert the list to a dictionary
    emotionOutput = emotion_labels[0]
    #get the emotion type and assign to a variable
    emotionType = emotionOutput.get('label')
    #get the emotion value and round to 2 decimal places
    emotionScore = round(emotionOutput.get('score'), 2)

    # get the tweet date
    tweetDate = info.created_at.strftime("%m-%d-%Y")
    # get the tweet time
    tweetTime = info.created_at.strftime("%H:%M:%S")

    # add all the data to an array
    data.append([userID, tweetDate, tweetTime, info.full_text, emotionType, emotionScore])

    # # check if the tweet already exists in database
    # item_details = tweets_collection.find()
    # for item in item_details:
    #     if item['Tweet'] == info.full_text :
    #         # if it exists fail
    #         print('tweet already exists')
    #     else :
    #         #add the tweets info to a variable
    #         data.append([userID, tweetDate, tweetTime, info.full_text, emotionType, emotionScore])

# convert data into a dataframe
df = pd.DataFrame(data, columns = columns)

print(df)
# # make the dataframe a dictionary
# data = df.to_dict(orient = "records")

# # send the dictionary to mongodb
# tweets_collection.insert_many(data)