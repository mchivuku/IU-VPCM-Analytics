#!/usr/bin/env python3
import requests

import sys
import pprint
import json
from settings import Settings
import os

import pandas as pd
## Get settings:
s = Settings()
stt = s.get_settings()

procssed_data_instagram = os.path.join(stt.processed_data_dir, stt.output_file)
user_follower_relationship_df = pd.read_excel(procssed_data_instagram,sheet_name="user_followers_relationship")
user_follower_relationship_df = user_follower_relationship_df.loc[:,['src_id', 'dst_id']]
user_follower_relationship_df.to_csv(os.path.join(stt.processed_data_dir,"follower_relationship.csv"),index=False)
