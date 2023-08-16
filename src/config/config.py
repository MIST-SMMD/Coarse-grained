# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: config
# @Author：Ryan Zhang(https://github.com/hz157),Uyoin (Yilong Wu) (https://github.com/uyoin)
# @DateTime: 3/3/2023 上午10:31

"""
    Centralized Configuration File
"""

# BAIDU API
BAIDU_API_HOST = 'https://api.map.baidu.com'  # Baidu Map Open Platform URL
# Baidu Maps Open Platform Access Key
BAIDU_API_AK = [{'wXt8jjWgphuL7q4YIfUReDVHer9jp8Hi': True},
      {'30PacN0iMGMvFno0na0xglGNXf1MWasI': True}]


# TENCENT API
TENCENT_API_HOST = 'https://apis.map.qq.com'
TENCENT_API_KEY = ''
TENCENT_API_SK = ''


# LOCAL FILE PATH
ORIGINAL_PATH = r'/content/MIST-SMMD/asserts/dataset/weibo_dataset.xlsx'
TEMP_SAVE_PATH = r'/content/MIST-SMMD/output/coarse_ist_temp.csv'
RESULT_SAVE_PATH = r'/content/MIST-SMMD/output/coarse_ist_result.xlsx'

# KEYWORD
TIME_KEYWORD = ["月","日","昨天","今天","前天"]  # Time-related keywords
FAC_REVERSE_KEYWORD = ['消防', '派出所']
