import requests

API_URL = "https://api-inference.huggingface.co/models/arpanghoshal/EmoRoBERTa"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers = headers, json = payload)
	return response.json()
	
emotionLabels = query({
	"inputs": "We were disappointed that they couldn't go.",
})
print(emotionLabels)

# strEmotionLabels = str(emotionLabels)
# strFormat = strEmotionLabels[3:-1492]
# strFormat = strFormat.replace("'", '')
# parts = strFormat.split(',')

# #get the emotion type and assign to a variable
# emotionType = parts[0]
# emotionType = emotionType[7:]
# #get the emotion value and round to 2 decimal places
# emotionValue = parts[1]
# emotionValue = emotionValue[8:]

# print(emotionType)
# print(type(emotion_labels))
# emotionOutput = dict(emotion_labels[0])
# print(emotionOutput)
# print(type(emotionOutput))
# emotionType = emotionOutput.get('label')
# print(emotionType)

# strOutput = str(output)
# strRem = strOutput[1:-1]

# print(strRem)

# import snscrape.modules.twitter as sntwitter
# import pandas as pd

# query = "(from:elonmusk) until:2020-01-01 since:2010-01-01"
# tweets = []
# limit = 10


# for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    
#     # print(vars(tweet))
#     # break
#     if len(tweets) == limit:
#         break
#     else:
#         tweets.append([tweet.date, tweet.username, tweet.content])
        
# df = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet'])
# print(df)

# snscrape --jsonl --progress --max-results 500 --since 2023-02-22 twitter-search "from:elonMusk until:2023-02-24" > text-query-tweets.json

# import os

# os.system('snscrape --jsonl --progress --max-results 500 --since 2023-02-22 twitter-search "from:elonMusk until:2023-02-24" > text-query-tweets.json')