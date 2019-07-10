#!/usr/bin/env python3

import requests

import sys
import pprint

import instagram_analytics


import json
from collections import namedtuple
from instagram_analytics import InstaAPI 

class Settings(object):

    @staticmethod
    def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

    def __init__(self, file="settings.json"):
        self.json_file = file

    def get_settings(self):
        with open(self.json_file, "r") as f:
            return json.load(f,object_hook=Settings._json_object_hook)

## Get settings:
s = Settings()
stt = s.get_settings()
api = InstaAPI(stt)
#api.get_user_info()
#api.get_tophashtags()
api.make_output_file()