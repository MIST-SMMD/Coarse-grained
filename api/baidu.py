# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: baidu
# @Author：Ryan Zhang    (https://github.com/hz157)
# @DateTime: 3/3/2023 上午10:31

"""
    百度地图开放平台
"""


import requests
from urllib import parse
from config import config
import hashlib
import json

from unit.coordinate import bd09_to_wgs84

# 百度地图开放平台 URL (修改./config/config.py)
host = config.BAIDU_API_HOST
# 百度地图开放平台访问密钥 (修改./config/config.py)
ak = config.BAIDU_API_AK


def calculateSn(queryStr: str):
    """
        sn签名计算
        https://lbsyun.baidu.com/index.php?title=lbscloud/api/appendix
    Args:
        queryStr: 请求地址

    Returns: sn签名
    """
    # 对queryStr进行转码，safe内的保留字符不转换
    encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    # 在最后直接追加上yoursk
    rawStr = encodedStr + ak
    return hashlib.md5(parse.quote_plus(rawStr).encode()).hexdigest()


def place_v2_search(query: str, region: str = "全国"):
    """
        地点检索V2.0 请求发起
        https://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi#service-page-anchor-1-3
    Args:
        query: 检索关键字
        region: 行政区划区域. Defaults to "全国".

    Returns: dict(地点名称，经纬度)
    """
    # 地点检索V2.0 URL地址
    apiURL = f'/place/v2/search?query={query}&region={region}&output=json&ak={ak}'
    # SN 计算与链接
    apiURL = apiURL + '&sn=' + calculateSn(apiURL)
    # 发起网络请求
    response = json.loads(requests.get(host + apiURL).text)
    # 请求结果
    result = []
    # 遍历返回数据
    for i in response['results']:
        # 构造列表（地点名称，经纬度，街景地图ID)
        try:
            result.append(
                {"name": i['name'],
                 'bd-09': {'lng': i['location']['lng'], 'lat': i['location']['lat']},
                 'street_id': i['street_id'] if 'street_id' in i.keys() else None})
        except Exception as e:
            print(e)
            return None
    if result:
        return result[0]    # 默认返回第一个，相关地较高
    return None
