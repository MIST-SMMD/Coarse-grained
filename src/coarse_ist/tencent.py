#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: new_mist
# @ File: tencent
# @ Time: 6/3/2023 上午8:44
# @ Author: hz157
# @ Github: https://github.com/hz157

"""
    腾讯位置服务
"""


import json
import requests
import hashlib

from src.config import config

# 腾讯地图开放平台 URL (修改./config/config.py)
host = config.TENCENT_API_HOST
# 腾讯地图开放平台访问密钥 (修改./config/config.py)
key = config.TENCENT_API_KEY
# 腾讯地图开放平台sig计算密钥 (修改./config/config.py)
sk = config.TENCENT_API_SK


def calculateSig(queryStr: str):
    """
        sig签名计算
        https://lbs.qq.com/faq/serverFaq/webServiceKey
    Args:
        queryStr: 请求地址

    Returns: md5 加密后的sig签名

    """
    return hashlib.md5(queryStr.encode('utf-8')).hexdigest()


def geocoder(query: str):
    """
        地址解析（地址转坐标） 请求发起
        https://lbs.qq.com/service/webService/webServiceGuide/webServiceGeocoder
    Args:
        query: 检索关键字

    Returns:

    """
    # 地点解析 URL地址
    apiURL = f'/ws/geocoder/v1/?address={query}&key={key}'
    # Sig 计算与链接
    apiURL = apiURL + '&sig=' + calculateSig(apiURL + sk)
    # 发起网络请求
    response = json.loads(requests.get(host + apiURL).text)
    if response['status'] != 0:
        return None
    # 请求结果
    result = {"name": response['result']['title'],
              'gcj-02': {'lng': response['result']['location']['lng'], 'lat': response['result']['location']['lat']}}
    return result
