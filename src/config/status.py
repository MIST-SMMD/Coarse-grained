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
    ner state enumeration
"""
    unrecognized = '1-unrecognized nerTime' # Normalized time not recognized - invalid parsing
    not_time_point = '1-Not Time Point' # Standardized type not time_point or time_span
    success = '2-Success Parse'

class SpaceStandardStatus(Enum):
    miss_gpe = '0-Missing GPE' # Missing GPE information
    foreign = '0-Foreign' # Foreign address
    nodata = '0-NoDATA' # no data

    invalid = '1-Invalid Parsing' # invalid parsing
    miss_part_gpe = '1-Missing part of gpe' # Missing part of gpe (e.g. province, city, district)
    uncertain = '1-Uncertain' # Uncertain whether parsing is correct or not

    success = '2-Success Parse'
    common = '2-Common Parse'



