#!/usr/bin/env python3

import numpy as np
import pandas as pd
import tweepy
import os

"""
Twitter OAuthorization code
"""


def twitter_oauth(authfile):
    with open(authfile, "r") as auth:
        ak = auth.readlines()

    auth.close()

    auth1 = tweepy.auth.OAuthHandler(ak[0].replace("\n", ""), ak[1].replace("\n", ""))
    auth1.set_access_token(ak[2].replace("\n", ""), ak[3].replace("\n", ""))
    return tweepy.API(auth1)

