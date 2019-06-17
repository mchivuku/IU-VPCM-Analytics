#!/usr/bin/env python3
import re

from textblob import TextBlob

## G
class TweetSentiment:
    def __init__(self):

        self.analysis = ""

    @staticmethod
    def clean_tweet(tweet_text):
        return ' '.join(
            re.sub(
                "(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)",
                " ",
                tweet_text).split())

    """
    Get sentiment of the tweets
    """
    def get_tweet_sentiment(self,tweet):
        self.analysis = TextBlob(TweetSentiment.clean_tweet(tweet))

        if self.analysis.sentiment.polarity>0:
            return "positive"
        elif self.analysis.sentiment.polarity==0:
            return "neutral"
        else:
            return "negative"


    """
    Get sentiment data
    """
    def get_tweet_sentiment_data(self,tweet):
        self.analysis = TextBlob(TweetSentiment.clean_tweet(tweet))
        return  self.analysis.sentiment