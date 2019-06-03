#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 16:12:51 2019

@author: zeski
"""

import json 




data = json.load(open("state_updated.json", "r"))

for i in data['features']: 
    print(type(i['properties']['Pop']))