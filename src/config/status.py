#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @ Project: new_mist
# @ File: status
# @ Time: 7/3/2023 上午9:30
# @ Author: Uyoin (Yilong Wu) (https://github.com/uyoin),Ryan Zhang (https://github.com/hz157)
# @ Github: https://github.com/hz157

"""
    ner状态枚举
"""

from enum import Enum


class TimeStandardStatus(Enum):
    """
        时间标准化状态提示
    """
    unrecognized = '1-unrecognized nerTime'  # 未识别到标准化时间-无效解析
    Not_time_point = '1-Not Time Point'# 标准化类型不为time_point 或是 time_span
    success = '2-Success Parse'

class SpaceStandardStatus(Enum):
    miss_gpe = '0-Missing GPE'  # 丢失GPE信息
    foreign = '0-Foreign'  # 国外地址
    nodata = '0-NoDATA'  # 无数据

    invalid = '1-Invalid Parsing'  # 无效解析
    miss_part_gpe = '1-Missing part of gpe'  # 丢失部分行政区信息(如省、市、区)
    uncertain = '1-Uncertain'  # 不确定是否解析正确

    success = '2-Success Parse'
    common = '2-Common Parse'



