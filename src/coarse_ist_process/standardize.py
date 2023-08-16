# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: standardize
# @Author：Uyoin (Yilong Wu) (https://github.com/uyoin),Ryan Zhang (https://github.com/hz157)
# @DateTime: 3/3/2023 下午12:50
import time
import datetime
from src.config import config
from jionlp import parse_time,parse_location,recognize_location
from src.config.status import TimeStandardStatus, SpaceStandardStatus

def del_Useless_timeWords(nerTimeFormat):
    """
            Remove time words that are not useful for this experiment (this experiment only needs to be accurate to the unit of "day") by traversing the time-related reverse keywords set in config/config.py.
        Args.
            Args: nerTimeFormat: spacy detected time-related label (TIME, DATE) text

        Returns: nerTimeFormat: text of the deleted timestamps (TIME,DATE)

    """
    flag = []

    for i in range(len(nerTimeFormat)):
        for KEYWORD in config.TIME_KEYWORD:
            if nerTimeFormat[i].find(KEYWORD) > 0:  # Time-related keywords, modify config/config.py
                break
            flag.append(i)  # Record the position of the nerTimeFormat element that does not belong to the time-related keyword nerTimeFormat, and iterate over the next
            break
    if len(flag) > 0:
        for i in range(len(flag)):
            del nerTimeFormat[flag[0]]
            del flag[0]
            # Since del drops nerTimeFormat by one element, if there's still a flag record, push the following element forward
            if len(flag) > 0:
                flag[0] = flag[0] - i - 1
    return nerTimeFormat


def time_standardize(nerTimeFormat, rawTimeFormat):
    """
        Time normalization
        Where time parsing is done using: jionlp.parse_time
        https://github.com/dongrixinyu/JioNLP/wiki/%E6%97%B6%E9%97%B4%E8%AF%AD%E4%B9%89%E8%A7%A3%E6%9E%90-%E8%AF%B4%E6%98%8E%E6%96%87%E6% A1%A3#user-content-%E6%97%B6%E9%97%B4%E8%AF%AD%E4%B9%89%E8%A7%A3%E6%9E%90
    Args.
        nerTimeFormat: text of the timestamp (TIME,DATE) detected by spacy
        rawTimeFormat: raw time of the tweet data

    Returns: param1: normalized time (year/month/day) param2: time normalized state

    """
    rawSplit = (rawTimeFormat.split(" ")[0]).split("-")  # Cutting time to just months and years
    st1_ymd = rawTimeFormat.split(" ")[0]  # [status1] Return time in case of unresolvable (YY-MM-DD)

    nerTimeFormat = del_Useless_timeWords(nerTimeFormat)

    if len(nerTimeFormat) == 0:
        return st1_ymd, TimeStandardStatus.unrecognized.value

    parseTime_list = []
    status_list = []
    try:
        for nerTime in nerTimeFormat:
            parseTime = parse_time(nerTime,
                                       time_base={'year': int(rawSplit[0]),
                                                  'month': int(rawSplit[1]),
                                                  'day': int(rawSplit[2])})
            # jionlp provides 4 types, this project only uses time_point as the time point to return
            if parseTime['type'] == 'time_point':
                # Determine if the parsed time is less than three days (valid time)
                parseDate = parseTime['time'][0].split(" ")[0]
                st1_ymd1 = tuple(time.strptime(st1_ymd, "%Y-%m-%d"))
                parseTime1 = tuple(time.strptime(parseDate, "%Y-%m-%d"))
                difference = (datetime.date(st1_ymd1[0], st1_ymd1[1], st1_ymd1[2]) - datetime.date(parseTime1[0],
                                                                                                   parseTime1[1],
                                                                                                   parseTime1[2])).days
                if -3 < difference < 3:
                    parseTime_list.append(parseDate)
                    status_list.append(TimeStandardStatus.success.value)
                    continue
            else:
                parseTime_list.append(st1_ymd)
                status_list.append(TimeStandardStatus.Not_time_point.value)

            if len(parseTime_list) == 0:
                parseTime_list.append(st1_ymd)
                status_list.append(TimeStandardStatus.unrecognized.value)
                continue
            parseTime_list = list(set(parseTime_list))
            status_list = list(set(status_list))
        # time_base parameter refers to the time base specified when parsing the time (in this case, the creation time of the microblog).
    except Exception as e:
        print(e)
        parseTime_list.append(st1_ymd)
        status_list.append(TimeStandardStatus.unrecognized.value)  # Standardized time not identified
    return parseTime_list, status_list  # Returns the table chase time and the time status returned by its jionlp


def create_full_space(data):
    """
        Fill the parsed address and check to determine what type the normalized address belongs to
    Args.
       data: Jionlp library recognize_location recognized return parameters

    Returns: locSet: set of standardized addresses after checking (list),status: set of standardized address status codes after checking (list)

    """
    locSet = []
    status = []
    for item in data:
        if item == "Missing GPE":
            continue
        loc = ''
        locSet.append(item["full_location"])
        for f in item["full_location"]:
            if f not in item['orig_location']:
                loc += f
        if len(loc) == 1:  # Invalid standardization if the difference between before and after standardization is only a single word (province, city, district).
            status.append(SpaceStandardStatus.invalid.value)
        else:
            if item['full_location'] == item['orig_location']:
                if item['county'] is None or item['city'] is None or item['province'] is None:
                    status.append(SpaceStandardStatus.miss_part_gpe.value)  # Lost part of gpe
                else:
                    status.append(SpaceStandardStatus.uncertain.value)  # If all is not lost, there's no way to know if it's right
                continue
            else:
                status.append(SpaceStandardStatus.success.value)
    return locSet, status


def Is_foreign(region):
    """
        Determine if the administrative region recognized by the Jionlp library recognize_location is a foreign country, region, or city.
    Args.
        region: Jionlp library recognize_location recognized return parameter

    Returns: 1: if yes, return the value 1

    """
    if region['foreign'] is not None and region['foreign'][0][0]["country"] != "中国":
        return 1


def space_standardize(labelData, rawData):
    """
        Spatial standardization
        Where address resolution is done using: parse_location
        https://github.com/dongrixinyu/JioNLP/wiki/Gadget-%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3#user-content-%E5%9C%B0%E5%9D%80%E8%A7%A3% E6%9E%90
        To determine whether the address is outside of mainland China: recognize_location:
        https://github.com/dongrixinyu/JioNLP/wiki/Gadget-%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3#user-content-%E6%96%B0%E9%97%BB%E5%9C%B0% E5%90%8D%E8%AF%86%E5%88%AB
    Args.
        labelData: all label information recognized by sentence NER
        rawData: crawl raw data dictionary

    Returns: locSet: standardized address set (list),status: standardized address status code set (list)

    """
    locSet = []
    status = []

    # Determine if there is a GPE (including label and IP address)
    if 'GPE' not in labelData.keys() or len(labelData['GPE']) == 0:
        if rawData['region'] == "nodata":
            return "Nodata", SpaceStandardStatus.miss_gpe  
        if Is_foreign(recognize_location(rawData['region'])) == 1:
            return 'Foreign', SpaceStandardStatus.foreign.value 
        GPE = rawData['region']
        for item in labelData['FAC']:
            locSet.append(parse_location(GPE + item, change2new=True, town_village=True))
        locSet, status = create_full_space(locSet)
    elif 'GPE' in labelData.keys():
        jio_region = []
        if rawData['region'] != "nodata":
            if Is_foreign(recognize_location(rawData['region'])) == 1:
                return 'Foreign', SpaceStandardStatus.foreign.value  
        flag = []
        for i in range(len(labelData['GPE'])):
            region = recognize_location(labelData['GPE'][i])
            if region['domestic'] is not None:
                if Is_foreign(recognize_location(rawData['region'])) == 1:
                    return 'Foreign', SpaceStandardStatus.foreign.value
                jio_region.append(region['domestic'][0][0])
            else:
                flag.append(i)
                locSet.append("Missing GPE")
                status.append(SpaceStandardStatus.miss_gpe.value)
        for i in sorted(flag, reverse=True):
            del labelData['GPE'][i]

        if len(labelData['GPE']) == 0:
            return locSet, status
        try:
            region_list = []
            if len(labelData['GPE']) >= 1:
                for region in jio_region:
                    region_temp = ''
                    for key in ['province', 'city', 'county']:
                        current_word = region[key]
                        if current_word is not None:
                            region_temp += current_word
                    region_list.append(region_temp)
        except Exception as e:
            print(e)
        flag = []
        for i in range(len(labelData['FAC'])):
            if len(labelData['FAC'][i]) <= 2:
                flag.append(i)
                continue
            for region in region_list:
                locSet.append(parse_location(region + labelData['FAC'][i], change2new=True, town_village=True))
        for i in sorted(flag, reverse=True):
            del labelData['FAC'][i]
        if rawData['region'] != "nodata":
            for item in labelData['FAC']:
                locSet.append(parse_location(rawData['region'] + item, change2new=True, town_village=True))
        locSet, status = create_full_space(locSet)

        if not locSet:
            return "Nodata", SpaceStandardStatus.nodata.value
    return locSet, status
