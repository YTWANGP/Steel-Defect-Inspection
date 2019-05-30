class MessageParser:
    #Returns the highest probablity tag in the json object (takes the output as json.loads as input)
    def highestProbabilityTagMeeting(self, allTagsAndProbability):
        highestProbabilityTag = 'none'
        highestProbability = 0
        for item in allTagsAndProbability:
            if item['Probability'] > highestProbability:
                highestProbability = item['Probability']
                highestProbabilityTag = item['Tag']
        return highestProbabilityTag