import requests

API_URL = "https://api-inference.huggingface.co/models/arpanghoshal/EmoRoBERTa"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers = headers, json = payload)
	return response.json()
	
emotionLabels = query({
	"inputs": "We were disappointed that they couldn't go.",
})

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
print(emotionLabels)
# print(type(emotion_labels))
# emotionOutput = dict(emotion_labels[0])
# print(emotionOutput)
# print(type(emotionOutput))
# emotionType = emotionOutput.get('label')
# print(emotionType)

# strOutput = str(output)
# strRem = strOutput[1:-1]

# print(strRem)