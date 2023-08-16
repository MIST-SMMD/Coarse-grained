# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: excel
# @Description: Excel 文件操作
# @Author：Uyoin(Yilong Wu) (https://github.com/uyoin)
# @DateTime: 3/18/2023 晚上08:08


"""
    Excel file read and write operations
"""

import os
import pandas as pd
import numpy as np

def read_excel(path):
    """
        Reading an Excel file
    Args.
        path: excel file path

    Returns:list or None

    """
    if os.path.exists(path):  
        return (np.array(pd.read_excel(path))).tolist()  
    else:  
        return None


def write_excel(path, data, fields):
    """
        Write to Excel file
    parameter:
        path: path to the excel file
        fields: list of fields

    Returns: true for success, false for failure

    """

    try:
        df = pd.DataFrame(data, columns=fields)
        df.to_excel(path)
        return True
    except Exception as e:
        print(e)
        return False
