#!/usr/bin/env python3

import sys


import sys
import pprint

import twitter_analytics, settings

## Get settings:
settings = settings.Settings()

api =  twitter_analytics.TweetsAPI(settings.get_settings())

api.get_twitter_user_profile()