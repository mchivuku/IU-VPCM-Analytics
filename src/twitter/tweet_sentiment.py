#!/usr/bin/env python3
import re
import string

from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

import nltk


from nltk.corpus import stopwords 
stopwords_english = stopwords.words('english')

from nltk.tokenize import TweetTokenizer 
from nltk.stem import PorterStemmer
from sklearn.externals import joblib
stemmer = PorterStemmer()

nltk.download("movie_reviews")
nltk.download('punkt')

## G
class TweetSentiment:
    def __init__(self):

        self.analysis = ""
        ## load model for prediction
        self.model = joblib.load("twitter_sentiment.pkl" )
        

    @staticmethod
    def clean_tweet(tweet_text):
        """
        1. remove retweet "RT"
        2. remove hyperlinks
        3. remove hashtags 
        4. remove stopwords
        5. remove emoticons 
        6. remove punctuation, full-stop and comma, exclamation sign etc.
        7. convert words to stem/base words using porter stemming algorithm
        """
        
        # Happy Emoticons
        emoticons_happy = set([':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
                                    ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
                                    '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
                                    'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
                                    '<3'])
        # Sad Emoticons
        emoticons_sad = set([':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
                                  ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
                                  ':c', ':{', '>:\\', ';('])
        # all emoticons (happy + sad)
        emoticons =  emoticons_happy.union(emoticons_sad)
        
        
        
        ## remove "RT"
        tweet = re.sub(r'^RT[\s]+','',tweet_text)
        
        ## remove hyperlinks
        tweet = re.sub(r'https?:\/\/.*[\r\n]*','',tweet)
        
        ## remove hashtags
        tweet = re.sub(r'#\w*', '', tweet)

        ## remove @ mentions
        tweet = re.sub('@[^\s]+','',tweet)
        
        # Remove words with 2 or fewer letters
        tweet = re.sub(r'\b\w{1,2}\b', '', tweet)

        # Remove whitespace (including new line characters)
        tweet = re.sub(r'\s\s+', ' ', tweet)
        # Remove single space remaining at the front of the tweet.
        tweet = tweet.lstrip(' ') 
        # Remove characters beyond Basic Multilingual Plane (BMP) of Unicode:
        tweet = ''.join(c for c in tweet if c <= '\uFFFF') 
        ## tokenize tweets
        # tokenize tweets
        tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
        tweet_tokens = tokenizer.tokenize(tweet)
        
        tweets_clean = []    
        for word in tweet_tokens:
            if (word not in stopwords_english and # remove stopwords
                word not in emoticons  and # remove emoticons
                word not in string.punctuation): # remove punctuation
                stem_word = stemmer.stem(word) # stemming word
                tweets_clean.append(stem_word)
                
        return " ".join(tweets_clean), tweets_clean
        
    
   
    """
    Get sentiment data
    """
    def get_tweet_sentiment_data(self,tweet):
        text, words = self.clean_tweet(tweet)
        analysis = TextBlob(text)
        
        polarity  = analysis.polarity
        subjectivity = analysis.subjectivity
        # formatting helper
        ## 0 = negative, 2 = neutral, 4 = positive
        if polarity < 0:
            sentiment = "Negative"
        elif polarity > 0 :
            sentiment = "Positive"
        else:
            sentiment = "Neutral"
        
        return  sentiment, text

