#!/usr/bin/env python3


import sys
import pprint

import twitter_analytics, settings

## Get settings:
settings = settings.Settings()

api =  twitter_analytics.TweetsAPI(settings.get_settings())

## Run user timeline
api.get_engagement_info()
