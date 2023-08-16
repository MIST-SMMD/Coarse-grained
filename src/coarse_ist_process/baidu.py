# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: baidu
# @Author：Uyoin (Yilong Wu) (https://github.com/uyoin),Ryan Zhang (https://github.com/hz157)
# @DateTime: 3/3/2023 上午10:31

"""
    Baidu Map Open Platform
"""

import re
import json
import hashlib
import requests
from urllib import parse
from src.config import config
from src.coarse_ist_process.coordinate import bd09_to_wgs84

# Baidu Maps Open Platform URL (modify. /config/config.py)
host = config.BAIDU_API_HOST
# Baidu Maps Open Platform Access Key (Modify . /config/config.py)
ak = config.BAIDU_API_AK

def calculateSn(queryStr: str,key:str):
    """
        SN signature calculation
        https://lbsyun.baidu.com/index.php?title=lbscloud/api/appendix
    Args.
        queryStr: request address

    Returns: SN signature
    """
    # transcode queryStr, reserved characters within safe are not converted
    encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
    # Append your sk directly at the end
    rawStr = encodedStr + key
    return hashlib.md5(parse.quote_plus(rawStr).encode()).hexdigest()


def place_v2_search(query: str, region: str = "全国"):
    """
        Location Retrieval V2.0 Request Initiation
        https://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi#service-page-anchor-1-3
    Args.
        query: search keywords
        region: Administrative region. Defaults to "country".

    Returns: dict(location, latitude, longitude)
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
    # Location Search V2.0 URL address
    apiURL = f'/place/v2/search?query={query}&region={region}&output=json&ak={key}'
    # SN calculations and links
    apiURL = apiURL + '&sn=' + calculateSn(apiURL,key)
    # Initiate web requests
    response = json.loads(requests.get(host + apiURL).text)
    result = []
    for i in response['results']:
        # Construct list (location name, latitude/longitude, street map ID)
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
        return result[0]
    return None
def Geocoder_v3_search(query:str,key:str):
    """
        Geocoding V3.0 Request Initiation
        https://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding
    Args.
        query: retrieve keyword
        key: your key

    Returns: str(WGS84 latitude and longitude) str(concatenation of confidence and level)
    """
    key = 'wXt8jjWgphuL7q4YIfUReDVHer9jp8Hi'
    apiURL = f'/geocoding/v3/?address={query}&output=json&ak={key}'
    apiURL = apiURL + '&sn=' + calculateSn(apiURL,key)
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
        Geocoding standardized addresses
    Args.
        stloc: standardized address (string or list)
        status: status of the standardized address

    Returns: loc_wgs84(WGS84 latitude and longitude of the standardized address) confidence_level(confidence level)
    """
    # Define regular expressions that match English
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
