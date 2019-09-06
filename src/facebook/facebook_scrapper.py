#!/usr/bin/env python3

import requests

import sys
import pprint
import os

from facebook_analytics  import FacebookAPI
  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings
import app_logger

logger = app_logger.get_logger("facebook-log",logfile="facebook.log")


## Get settings:
s = settings.Settings()
stt = s.get_settings()
api = FacebookAPI(stt)
#api.get_user_info()
#api.get_tophashtags()
api.make_output_file()