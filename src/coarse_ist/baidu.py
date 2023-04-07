# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: baidu
# @Author：Uyoin (Yilong Wu) (https://github.com/uyoin),Ryan Zhang (https://github.com/hz157)
# @DateTime: 3/3/2023 上午10:31

"""
    百度地图开放平台
"""

import re
import json
import hashlib
import requests
from urllib import parse
from src.config import config
from src.coarse_ist.coordinate import bd09_to_wgs84

# 百度地图开放平台 URL (修改./config/config.py)
host = config.BAIDU_API_HOST
# 百度地图开放平台访问密钥 (修改./config/config.py)
ak = config.BAIDU_API_AK

def calculateSn(queryStr: str,key:str):
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
    rawStr = encodedStr + key
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
    position = 0
    key = ''
    for i in range(len(ak)):
        for d in ak[i]:
            if ak[i][d]:
                key = d
                position = i
                break
    if key == '':
        return '无可用ak'
    # 地点检索V2.0 URL地址
    apiURL = f'/place/v2/search?query={query}&region={region}&output=json&ak={key}'
    # SN 计算与链接
    apiURL = apiURL + '&sn=' + calculateSn(apiURL,key)
    # 发起网络请求
    response = json.loads(requests.get(host + apiURL).text)
    # 请求结果
    result = []
    # 遍历返回数据
    for i in response['results']:
        # 构造列表（地点名称，经纬度，街景地图ID)
        if i['status'] == 302 and '天配额超限，限制访问' in i['message']:
            ak[position][key] = False
            return
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
def Geocoder_v3_search(query:str,key:str):
    """
        地理编码V3.0 请求发起
        https://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding
    Args:
        query: 检索关键字
        key: 你的key

    Returns: str(WGS84经纬度)      str(置信度和级别的连接)
    """
    key = 'wXt8jjWgphuL7q4YIfUReDVHer9jp8Hi'
    # 地点检索V2.0 URL地址
    apiURL = f'/geocoding/v3/?address={query}&output=json&ak={key}'
    # SN 计算与链接
    apiURL = apiURL + '&sn=' + calculateSn(apiURL,key)
    # 发起网络请求
    response = json.loads(requests.get(host + apiURL).text)

    if not isinstance(response, dict):
        return
    position = 0
    if response['status'] != 0:
        if response['status'] == "302":
            ak[position][key] = False
        print(response)
        return response

    try:
        lng = response['result']['location']["lng"]
        lat = response['result']['location']["lat"]
        confidence = response['result']["confidence"]
        level = response['result']["level"]
    except Exception as e:
        print(e)
        return None
    temp = bd09_to_wgs84(lng,lat)
    loc_wgs84 = str(temp[0]) + "," + str(temp[1])
    confidence_level = str(confidence) + "  " +level
    return loc_wgs84,confidence_level


def Geocoder_v3_search_stloc(stloc,status):
    """
        对标准化的地址进行地理编码
    Args:
        stloc: 标准化后的地址（字符串或列表）
        status: 标准化地址的状态

    Returns: loc_wgs84(标准化后地址的WGS84经纬度)      confidence_level(置信度级别)
    """
    # 定义匹配英文的正则表达式（考虑了英文间空格的情况）
    pattern_en = re.compile(r'^[a-zA-Z ]+$')

    key = ''
    for i in range(len(ak)):
        for d in ak[i]:
            if ak[i][d]:
                key = d
                position = i
                break
    if key == '':
        return '无可用ak'

    if isinstance(stloc, list):
        loc_wgs84 = []
        confidence_level = []
        i = 0
        for loc in stloc:
            if pattern_en.match(loc):
                loc_wgs84.append("Nodata")
                confidence_level.append("Nodata")
                continue
            status_id = status[i].split("-")
            if status_id[0] != "1" and status_id[0] != "2":
                loc_wgs84.append("Nodata")
                confidence_level.append("No conversion")
                continue
            info = Geocoder_v3_search(loc,key)
            if isinstance(info, dict):
                loc_wgs84.append(info)
                confidence_level.append(info)
            else:
                loc_wgs84.append(info[0])
                confidence_level.append(info[1])
            i+=1
    elif isinstance(stloc, str):
        if pattern_en.match(stloc):
            loc_wgs84 = "Nodata"
            confidence_level = "Nodata"
            return loc_wgs84,confidence_level
        status_id = status.split("-")
        if status_id[0] != "1" and status_id[0] != "2":
            loc_wgs84 = "Nodata"
            confidence_level = "No conversion"
            return loc_wgs84,confidence_level

        loc_wgs84,confidence_level = Geocoder_v3_search(stloc,key)

    return loc_wgs84,confidence_level
# import pandas as pd
# path = r"C:\Users\LENOVO\Documents\WeChat Files\a183873588\FileStorage\File\2023-03\卢碧报道涝点.xlsx"
# df = pd.read_excel(path )
# # 选择需要读取的列，并跳过第一行
# column_name = '地点'
# data = df[column_name].tolist()
#
# i = 0
# key ="30PacN0iMGMvFno0na0xglGNXf1MWasI"
# x_wgs84 = []
# y_wgs84 = []
# confidence_level=[]
# loc1 = []
# import pandas as pd
# for loc in data:
#     info = Geocoder_v3_search(loc,key)
#     x_wgs84 .append(info[0].split(",")[0])
#     y_wgs84.append(info[0].split(",")[1])
#     confidence_level.append(info[1])
#     loc1.append(loc)
#     i+=1
# # 创建DataFrame
# df = pd.DataFrame({'loc': loc1, 'x_wgs84': x_wgs84, 'y_wgs84': y_wgs84,'confidence_level': confidence_level})
# # 写入Excel文件
# df.to_excel('[wgs84]卢碧报道涝点.xlsx', index=False)