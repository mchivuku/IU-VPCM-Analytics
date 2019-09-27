#!/usr/bin/env python3

import json

from collections import  namedtuple

class Settings(object):

    @staticmethod
    def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

    def __init__(self, file="settings.json"):
        self.json_file = file

    def get_settings(self):
        with open(self.json_file, "r") as f:
            return json.load(f,object_hook=Settings._json_object_hook)
