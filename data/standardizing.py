# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: standardizing
# @Author：Ryan Zhang    (https://github.com/hz157)
# @DateTime: 3/3/2023 下午12:50
import jionlp as jio
import datetime
import time
from config import config
from unit.status import TimeStandardStatus, SpaceStandardStatus


def del_Useless_timeWords(nerTimeFormat):
    """
            删除对本实验无用时间词（本实验只需精确到“日”单位），通过遍历config/config.py设置的时间相关反向关键字(Useless words)
        Args:
            nerTimeFormat:  spacy 所检测到的时间相关标签(TIME,DATE)文本

        Returns:    nerTimeFormat：删除后的时间相关标签(TIME,DATE)文本

        """
    flag = []

    for i in range(len(nerTimeFormat)):
        for KEYWORD in config.TIME_KEYWORD:
            if nerTimeFormat[i].find(KEYWORD) > 0:  # 时间相关关键字，修改config/config.py
                break
            flag.append(i)  # 记录不属于时间相关关键字nerTimeFormat元素的位置,并遍历下一个
            break
    if len(flag) > 0:
        for i in range(len(flag)):
            del nerTimeFormat[flag[0]]
            del flag[0]
            # 因为del掉nerTimeFormat一个元素，所以如果还有flag记录，把后面的元素往前推
            if len(flag) > 0:
                flag[0] = flag[0] - i - 1
    return nerTimeFormat


def time_standardization(nerTimeFormat, rawTimeFormat):
    """
        时间语义解析， 采用jionlp.parse_time
        https://github.com/dongrixinyu/JioNLP/wiki/%E6%97%B6%E9%97%B4%E8%AF%AD%E4%B9%89%E8%A7%A3%E6%9E%90-%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3#user-content-%E6%97%B6%E9%97%B4%E8%AF%AD%E4%B9%89%E8%A7%A3%E6%9E%90
    Args:
        nerTimeFormat:  spacy 所检测到的时间相关标签(TIME,DATE)文本
        rawTimeFormat:  微博数据原生的时间

    Returns:    param1：标准化后的时间（年/月/日）  param2：时间标准化的状态

    """
    rawSplit = (rawTimeFormat.split(" ")[0]).split("-")  # 时间切割至只剩年月日
    st1_ymd = rawTimeFormat.split(" ")[0]  # [status1]无法解析情况下的返回时间（年-月-日）

    nerTimeFormat = del_Useless_timeWords(nerTimeFormat)

    if len(nerTimeFormat) == 0:
        return st1_ymd, TimeStandardStatus.unrecognized  # 文章没有TIME标签，或者刚刚删完啦，无法标准化的时间（不满足实验需求）

    parseTime_list = []
    status_list = []
    try:
        # 遍历解析时间
        for nerTime in nerTimeFormat:
            parseTime = jio.parse_time(nerTime,
                                       time_base={'year': int(rawSplit[0]),
                                                  'month': int(rawSplit[1]),
                                                  'day': int(rawSplit[2])})
            # jionlp 提供了4种 type, 该项目只采用time_point(时间点)作为时间点返回
            if parseTime['type'] == 'time_point' :
                # 判断解析得时间是否小于三天（有效时间）
                parseDate = parseTime['time'][0].split(" ")[0]
                st1_ymd1 = tuple(time.strptime(st1_ymd,"%Y-%m-%d"))
                parseTime1 = tuple(time.strptime(parseDate, "%Y-%m-%d"))
                difference = (datetime.date(st1_ymd1[0],st1_ymd1[1],st1_ymd1[2]) - datetime.date(parseTime1[0],parseTime1[1],parseTime1[2])).days
                if -3 < difference < 3:
                    parseTime_list.append(parseDate)
                    status_list.append(TimeStandardStatus.success)
                    continue
            else:
                parseTime_list.append(st1_ymd)
                status_list.append(TimeStandardStatus.Not_time_point)  # 没有标准化时间

            if len(parseTime_list) == 0:
                status_list.append(TimeStandardStatus.unrecognized)
                continue
            # 去重
            parseTime_list = list(set(parseTime_list))
            status_list = list(set(status_list))
        # time_base 参数其指解析时间时指定的时间基点（这里为微博的创建时间）
    except Exception as e:  # 异常捕获
        print(e)
        parseTime_list.append(st1_ymd)
        status_list.append(TimeStandardStatus.unrecognized)  # 未识别到标准化时间
    return parseTime_list, status_list  # 返回表追时间及其jionlp所返回的时间状态


def create_full_space(data):
    locSet = []
    loc = ''
    status = []
    for item in data:
        for f in item["full_location"]:
            if f not in item['orig_location']:  # 去重
                loc += f
        if len(loc) == 1:  # 如果标准化前后区别只有单字（省、市、区），则是无效标准化，直接返回
            return locSet, SpaceStandardStatus.invalid
        if item['full_location'] == item['orig_location']:
            if item['county'] is None:
                status.append(SpaceStandardStatus.miss_country)  # 丢失国家信息
            elif item['city'] is None:
                status.append(SpaceStandardStatus.miss_city)  # 丢失城市信息
            elif item['province'] is None:
                status.append(SpaceStandardStatus.miss_province)  # 丢失省份信息
            locSet.append(item['full_location'])
            continue
        else:
            status.append(SpaceStandardStatus.success)
            locSet.append(item['full_location'])
    return locSet, status


def spacy_standization(labelData, rawData):
    locSet = []
    statusSet = []
    # 判断是否有GPE(包括标签和IP地址)
    if 'GPE' not in labelData.keys():
        if rawData['region'] == "nodata":
            return "Nodata", SpaceStandardStatus.miss_gpe  # 丢失GPE信息
        #
        GPE = rawData['region']
        for item in labelData['FAC']:
            locSet.append(jio.parse_location(GPE + item, change2new=True, town_village=True))
        locSet, status = create_full_space(locSet)
        if not locSet:
            statusSet.append(SpaceStandardStatus.common)
        else:
            statusSet.append("返回个寂寞")
    elif 'GPE' in labelData.keys():
        jio_region = []
        # 补全每个GPE并判断是否国外
        for item in labelData['GPE']:
            region = jio.recognize_location(item)
            if region['foreign'] is not None and region['foreign'][0][0]["country"] != "中国":
                return 'Foreign', SpaceStandardStatus.foreign  # 中国大陆境外数据直接丢弃
            try:
                jio_region.append(region['domestic'][0][0])
            except Exception as e:
                # 说不定可以直接越过
                # print(e)
                print(item + " is unrecognized")

        try:
            region = ''
            region_list = []
            if len(labelData['GPE']) >= 1:
                # 将补全GPE后的字典组合成一个新的region_list
                for key in ['province', 'city', 'county']:
                    for i in range(len(jio_region)):
                        if key in jio_region[i].keys():
                            current_word = jio_region[i][key]
                            if current_word is not None:
                                region += current_word
                region_list.append(region)
        except Exception as e:
            print(e)
        for item in labelData['FAC']:
            for region in region_list:
                locSet.append(jio.parse_location(region + item, change2new=True, town_village=True))
        if rawData['region'] != "nodata":
            for item in labelData['FAC']:
                locSet.append(jio.parse_location(rawData['region'] + item, change2new=True, town_village=True))
        locSet, status = create_full_space(locSet)
        if not locSet:
            return "Nodata", SpaceStandardStatus.nodata  # 无数据
        else:
            statusSet.append(SpaceStandardStatus.success)
    return locSet,statusSet