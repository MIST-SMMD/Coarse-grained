# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: config
# @Author：Ryan Zhang    (https://github.com/hz157)
# @DateTime: 3/3/2023 上午10:31

"""
    集中配置文件
"""

# BAIDU API
BAIDU_API_HOST = 'https://api.map.baidu.com'  # 百度地图开放平台 URL
BAIDU_API_AK = ''  # 百度地图开放平台访问密钥

# GOOGLE API


# TENCENT API
TENCENT_API_HOST = 'https://apis.map.qq.com'
TENCENT_API_KEY = ''
TENCENT_API_SK = ''


# LOCAL FILE PATH
ORIGINAL_PATH = r'dataset/[textcat-screened]weibo_dataset.xlsx'
SAVE_PATH = r'dataset/dateset3.csv'

# KEYWORD
TIME_KEYWORD = ["月","日","昨天","今天","前天"]  # 时间相关关键字
FAC_REVERSE_KEYWORD = ['消防', '派出所']