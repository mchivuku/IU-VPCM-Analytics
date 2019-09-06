#!/usr/bin/env python3

import requests

import sys
import pprint

import instagram_analytics


import json
from collections import namedtuple
from instagram_analytics import InstaAPI 
from settings import Settings


## Get settings:
s = Settings()
stt = s.get_settings()
api = InstaAPI(stt)
#api.get_user_info()
api.make_output_file()
