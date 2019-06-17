#!/usr/bin/env python3

import csv
import json
import math
import pprint
import sys
import os
import pandas as pd
import tweepy
from tweet_parser.tweet import Tweet as tweet_parser_tweet
from datetime import datetime
import time
import yaml

## Local files and imports
from prettytable import unicode

import warnings
warnings.filterwarnings("ignore")

from twitter_auth import twitter_oauth
from twitter_logging import get_logger
from tweet_sentiment import TweetSentiment

from gnip_insights_interface.engagement_api import query_tweets, get_n_months_after_post

## Class contains various methods for getting tweets from twitter
class TweetsAPI:

    def __init__(self, settings, sentiment_analyzer=TweetSentiment):
        """
        init class
        :param settings: settings object
        """
        self.settings = settings  ## read settings file
        self.start_date = datetime.strptime(self.settings.start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(self.settings.end_date, '%Y-%m-%d')
        self.username = self.settings.username

        self.auth = twitter_oauth(settings.auth_file)
        self.api = self.auth


        self.logger = get_logger("TweetsAPI")
        self.sentiment_analyzer = sentiment_analyzer()

        self.engagement_url = "https://data-api.twitter.com/insights/engagement"



    """
    Get tweets from user timeline
    """

    def get_user_timeline(self):
        tweets = []

        try:
            print("Downloading '" + self.username + "' timeline")

            tmp_tweets = self.api.user_timeline(screen_name=self.username)
            for tweet in tmp_tweets:
                if tweet.created_at < self.end_date and tweet.created_at > self.start_date:
                    tweets.append(tweet)

            ## Keep fetching the tweets
            while (tmp_tweets[-1].created_at > self.start_date):
                print("Last Tweet @" , tmp_tweets[-1].created_at, " - fetching some more tweets")
                tmp_tweets = self.api.user_timeline(self.username, max_id=tmp_tweets[-1].id)
                for tweet in tmp_tweets:
                    if tweet.created_at < self.end_date and tweet.created_at > self.start_date:
                        tweets.append(tweet)



            ## write to csv file
            csvFile = open(os.path.join(self.settings.raw_data_dir,self.settings.user_timeline_results_filename), "w")
            csvWriter = csv.writer(csvFile)
            csvWriter.writerow(["created",
                                "time",
                                "text",
                                "polarity",
                                "subjectivity",

                                "tweet_id",
                                "truncated",
                                "user",
                                "user_followers_count",
                                "user_friends_count",
                                "user_favourites_count",
                                "user_statuses_count",


                                "retweeted_status",
                                "month",
                                "year",

                                "retweet_count",
                                "favorite_count",
                                "reply_count",

                                "at_mentions",
                                "hashtags",
                                "urls",


                                "source",
                                "lat",
                                "long",
                                "tweet_type"

                                ])

            ## save Tweets
            for tweet in tweets:
                tweet = tweet._json


                ##Sat Jun 08 20:43:04 +0000 2019
                created_at = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y').date()
                time = datetime.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y').time()

                tweet_dec_text = tweet["text"].encode('ascii', errors='ignore')

                sentiment_data = self.sentiment_analyzer.get_tweet_sentiment_data(tweet["text"])
                polarity = sentiment_data[0]
                subjectivity = sentiment_data[1]

                tweet_id = str(tweet["id_str"])
                truncated = tweet["truncated"]

                user = tweet["user"]["screen_name"]
                user_followers_count = tweet["user"]["followers_count"]
                user_friends_count = tweet["user"]["friends_count"]
                user_favourites_count = tweet["user"]["favourites_count"]
                user_statuses_count = tweet["user"]["statuses_count"]


                if "retweeted_status" in tweet:
                    retweeted_status = "RETWEET"

                    retweeted_user = tweet['retweeted_status']['user']['id_str']
                    retweeted_user_description = tweet['retweeted_status']['user']['description']
                    retweeted_user_screen_name = tweet['retweeted_status']['user']['screen_name']
                    retweeted_user_followers_count = tweet['retweeted_status']['user']['followers_count']
                    retweeted_user_listed_count = tweet['retweeted_status']['user']['listed_count']
                    retweeted_user_statuses_count = tweet['retweeted_status']['user']['statuses_count']
                    retweeted_user_location = tweet['retweeted_status']['user']['location']
                    retweeted_tweet_created_at_text = tweet['retweeted_status']['created_at']
                    retweeted_tweet_created_at = datetime.strptime(retweeted_tweet_created_at_text,
                                                                   '%a %b %d %H:%M:%S +0000 %Y')

                else:
                    retweeted_status = ""
                    retweeted_user = ""
                    retweeted_user_description = ""
                    retweeted_user_screen_name = ""
                    retweeted_user_followers_count = ""
                    retweeted_user_listed_count = ""

                    retweeted_user_statuses_count = ""
                    retweeted_user_location = ""
                    retweeted_tweet_created_at_text = ""
                    retweeted_tweet_created_at = ""

                words = tweet_dec_text.split()
                num_words = len(words)

                month = created_at.strftime('%m')
                year = created_at.strftime("%Y")

                retweet_count = tweet['retweet_count']
                favorite_count = tweet['favorite_count']

                try:
                    reply_count = tweet["reply_count"]
                except:
                    reply_count = 0


                ## hashtags and urls, mentions
                urls_count = len(tweet['entities']['urls'])
                hashtags_count = len(tweet['entities']['hashtags'])
                mentions_count = len(tweet['entities']['user_mentions'])
                source = tweet['source']

                ## expand entities to get urls, hashtags, and mentions
                entities_urls, entities_expanded_urls, entities_hashtags, entities_mentions = [], [], [], []
                for each in tweet['entities']['urls']:
                    if 'url' in each:
                        url = each["url"]
                        expanded_url = each["expanded_url"]
                        entities_urls.append(url)
                        entities_expanded_urls.append(expanded_url)
                    else:
                        print("No urls")

                for hashtag in tweet['entities']['hashtags']:
                    if 'text' in hashtag:
                        tag = hashtag['text']
                        entities_hashtags.append(tag)
                    else:
                        print("No hashtags")

                for at in tweet['entities']['user_mentions']:
                    if 'screen_name' in at:
                        mention = at['screen_name']
                        entities_mentions.append(mention)
                    else:
                        print("No mentions")

                entities_mentions = ", ".join(entities_mentions)
                entities_hashtags = ", ".join(entities_hashtags)
                entities_urls = ", ".join(entities_urls)
                entities_expanded_urls = u", ".join(entities_expanded_urls)

                video_link = 0
                photo_link = 0
                twitpic = 0

                if "vimeo" in entities_expanded_urls or "youtube" in entities_urls or "youtu" in entities_expanded_urls or "vine" in entities_expanded_urls:
                    video_link = 1

                if 'twitpic' in entities_expanded_urls:
                    twitpic = 1

                if 'twitpic' in entities_expanded_urls or 'instagram' in entities_expanded_urls or 'instagr' in entities_expanded_urls:
                    photo_link = 1

                """entities_urls = unicode(entities_urls)
                entities_expanded_urls = unicode(entities_expanded_urls)
                entities_hashtags = unicode(entities_hashtags)
                entities_mentions = unicode(entities_mentions)
                """

                if "media" in tweet["entities"]:
                    entities_media_count = len(tweet["entities"]["media"])
                else:
                    entities_media_count = ''


                try:
                    lat = tweet["coordinates"]["coordinates"][0]
                    long = tweet["coordinates"]["coordinates"][1]
                except:
                    lat = ""
                    long = ""


                tweet_type = "quote" if tweet["is_quote_status"] else ( "retweet" if retweeted_status == "RETWEET" else "tweet")

                csvWriter.writerow(
                    [created_at, time,tweet["text"], polarity, subjectivity,
                     tweet_id,
                     truncated,
                     user, user_followers_count,user_friends_count,user_favourites_count,user_statuses_count,
                     retweeted_status,
                     month, year, retweet_count, favorite_count, reply_count,
                     entities_mentions, entities_hashtags, entities_urls,

                     source, lat,long, tweet_type])



        except tweepy.TweepError as e:
            if e.api_code == 429:
                print("[ERROR: TWEEPY API] Too many requests. Wait some minutes.")
            else:
                print("[ERROR: TWEEPY API]")
            sys.exit()
        except Exception as e:
            print("[ERROR]: ", e)
            sys.exit()


    """
    Get User engagements / TODO Check
    """
    def get_engagement_info(self):
        config = yaml.load(open(self.settings.engagement_config_yaml_file))
        groupings = config["engagement"]["groupings"]
        engagement_types = config['engagement']['engagement_types']



        endpoint = 'totals'
        max_tweet_ids = 250

        results = query_tweets([1137002128684322816],
                               groupings,
                               endpoint,
                               engagement_types,
                               max_tweet_ids,
                               (None, None),
                               )

        sys.stdout.write(json.dumps(results) + '\n')


    """
    Paginate for Cursor
    """
    def paginate(self,items,n):
        for i in range(0, len(items), n):
            yield items[i:i + n]

    """
    Get User profile, compute reach

    """
    def get_twitter_user_profile(self):
        MAX_FRIENDS = 15000

        client = self.api
        profile = client.get_user(screen_name=self.settings.username)
        user_profile = profile._json

        max_pages = math.ceil(MAX_FRIENDS / 5000)
        sum_reach = 0
        for followers in tweepy.Cursor(client.followers_ids,
                                screen_name=self.settings.username).pages(max_pages):
            for chunk in self.paginate(followers, 100):
                users = client.lookup_users(user_ids=chunk)
                for user in users:
                    sum_reach+=user._json["followers_count"]


        avg_followers = round(sum_reach/user_profile["followers_count"], 2)
        csvFile = open(os.path.join(self.settings.raw_data_dir, self.settings.user_profile_results_filename), "w")
        csvWriter = csv.writer(csvFile)

        csvWriter.writerow(["user_id", "name", "screen_name", "followers_count", "friends_count",
                            "favourites_count","statuses_count","total_reach","avg_follower_cnt"])

        csvWriter.writerow([user_profile["id_str"],user_profile["name"],user_profile["screen_name"],
                            user_profile["followers_count"],user_profile["friends_count"],
                            user_profile["favourites_count"],
                            user_profile["statuses_count"],
                            sum_reach,avg_followers])




