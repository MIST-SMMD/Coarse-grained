#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: new_mist
# @ File: tencent
# @ Time: 6/3/2023 上午8:44
# @ Author: hz157
# @ Github: https://github.com/hz157

"""
    Tencent Location Services
"""


import json
import requests
import hashlib

from src.config import config

# Tencent Maps Open Platform URL (modify . /config/config.py)
host = config.TENCENT_API_HOST
# Tencent Maps Open Platform Access Key (Modify . /config/config.py)
key = config.TENCENT_API_KEY
# Tencent Maps Open Platform sig key (Modify . /config/config.py)
sk = config.TENCENT_API_SK


def calculateSig(queryStr: str):
    """
        sig signature calculation
        https://lbs.qq.com/faq/serverFaq/webServiceKey
    Args.
        queryStr: request address

    Returns: md5 encrypted sig signature

    """
    return hashlib.md5(queryStr.encode('utf-8')).hexdigest()


def geocoder(query: str):
    """
        Address resolution (address to coordinates) Request initiation
        https://lbs.qq.com/service/webService/webServiceGuide/webServiceGeocoder
    Args.
        query: Retrieve keywords

    Returns.

    """
    apiURL = f'/ws/geocoder/v1/?address={query}&key={key}'
    apiURL = apiURL + '&sig=' + calculateSig(apiURL + sk)
    response = json.loads(requests.get(host + apiURL).text)
    if response['status'] != 0:
        return None
    result = {"name": response['result']['title'],
              'gcj-02': {'lng': response['result']['location']['lng'], 'lat': response['result']['location']['lat']}}
    return result
