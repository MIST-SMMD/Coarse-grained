# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: excel
# @Description: Excel 文件操作
# @Author：Uyoin(Yilong Wu) (https://github.com/uyoin)
# @DateTime: 3/18/2023 晚上08:08


"""
    CSV文件读写操作
"""

import os
import pandas as pd
import numpy as np

def read_excel(path):
    """
        读取Excel文件
    Args:
        path: excel文件路径

    Returns:list or None

    """
    if os.path.exists(path):  # 判断excel是否存在
        return (np.array(pd.read_excel(path))).tolist()  # 用pd库读为df再从np.array转到list
    else:  # 不存在返回空值
        return None


def write_excel(path, data, fields):
    """
        写入Excel文件
    Args:
        path: excel文件路径
        fields: 字段list

    Returns: True Success, False Fail

    """

    try:
        df = pd.DataFrame(data, columns=fields)
        df.to_excel(path)
        return True
    except Exception as e:
        print(e)
        return False
