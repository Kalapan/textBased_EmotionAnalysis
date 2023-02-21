from http import client
from dotenv import dotenv_values, load_dotenv
import tweepy
import pandas as pd
from pymongo import MongoClient
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline
import sys
import unittest

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
#assign which model to use
emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')

#assign the users twitter id to userID
# userID = str(sys.argv[1])
userID = 'JoeBiden'

#parameters set to get the tweets
tweets = api.user_timeline(screen_name = userID, count = 200, include_rts = False, exclude_replies = True, tweet_mode = 'extended')

#set the column title which the tweets will be saved in
columns = ['Twitter_ID','Date', 'Time', 'Tweet', 'Emotion', 'Value']
#make an array to hold the data
data = []
tweetTextTest = ''

#get the latest tweet and format
for info in tweets [:2]:
    tweetTextTest = info.full_text
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

    # check if the tweet already exists in database
    item_details = tweets_collection.find_one({
        "Tweet": info.full_text,
    })
    # if tweet does not exist in database
    if item_details is None:
        # add all the data to an array
        data.append([userID, tweetDate, tweetTime, info.full_text, emotionType, emotionScore])
        # convert data into a dataframe
        df = pd.DataFrame(data, columns = columns)
        # make the dataframe a dictionary
        data = df.to_dict(orient = "records")
        # send the dictionary to mongodb
        tweets_collection.insert_many(data)
        print("Data inserted into the database.")
    else:
        print("Data already exists in the database.")

#Tests
# check if userid has a value
# class TestTextVariable(unittest.TestCase):
#     def setUp(self):
#         self.variable = userID

#     def test_text_variable(self):
#         self.assertIsNotNone(self.variable, 'Variable does not have a value!')
#         print("UserID exists")

# test if connection to mongodb is established
# class TestMongoDBConnection(unittest.TestCase):
#     def test_connection(self):
#         client = MongoClient(config["MongoLogIn"])
#         self.assertTrue(client.server_info())
#         print('Database connection successful')

# test if data output is a list
# class TestDictionary(unittest.TestCase):
#     def test_get_dictionary(self):
#         result = data
#         self.assertIsInstance(result, list)
#         print('Output of python script is list')

# test if tweet is pulled from twitter api and if the tweet is a string
# class TestTwitterAPI(unittest.TestCase):
#     def test_tweet_retrieval(self):
#         self.assertGreater(len(tweetTextTest), 0)
#         print("A tweet was retrieved using Twitter API.")
#         self.assertIsInstance(tweetTextTest, str)
#         print("The tweet is a string.")

# test if the analyzed tweets are added to the mongodb database
# class TestMongoDBInsertion(unittest.TestCase):
#     def setUp(self):
#         self.client = MongoClient(config["MongoLogIn"])
#         self.db = self.client['User']
#         self.collection = self.db['tweets_information']

#     def test_data_insertion(self):
#         result = self.collection.insert_many(data)
#         self.assertTrue(result.acknowledged, 'Data insertion failed!')
#         print("Tweets are inserted successfully")

# if __name__ == '__main__':
#     unittest.main()