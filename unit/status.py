#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: new_mist
# @ File: status
# @ Time: 7/3/2023 上午9:30
# @ Author: hz157
# @ Github: https://github.com/hz157

"""
    ner状态枚举
"""

from enum import Enum


class TimeStandardStatus(Enum):
    """
        时间标准化状态提示
    """
    unrecognized = '1-Unrecognized nerTime'  # 未识别到标准化时间
    Not_time_point = '1-Not time point'# 标准化类型不为time_point 或是 time_span
    success = '2-Success parse'

class SpaceStandardStatus(Enum):
    miss_gpe = '0-Missing GPE'  # 丢失GPE信息
    foreign = '0-Foreign'  # 国外地址
    nodata = '0-NoDATA'  # 无数据
    invalid = '0-Invalid standardization'  # 无效标准化
    miss_country = '1-missing country'  # 丢失国家信息
    miss_city = '1-missing city'  # 丢失城市信息
    miss_province = '1-missing province'  # 丢失省份信息
    success = '2-Success parse'
    common = '2-Common parse'



