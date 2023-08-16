# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: csv
# @Description: CSV 文件操作
# @Author：Ryan Zhang(https://github.com/hz157),Uyoin (Yilong Wu) (https://github.com/uyoin)
# @DateTime: 3/3/2023 上午10:31


"""
    CSV file read and write operations
"""

import os
import csv


def read_csv(path, encoding: str = 'utf-8'):
    """
        Reading a CSV file
    Args.
        path: path to csv file
        encoding: encoding format. Defaults to 'utf-8'.

    Returns:list or None

    """
    result = []
    if os.path.exists(path): 
        with open(path, 'r', encoding=encoding) as f:
            lines = csv.reader(f)
            next(lines)
            for line in lines:
                result.append(line)
        return result
    else: 
        return None


def write_csv(path, fields, encoding: str = 'utf-8-sig'):
    """
        Write to CSV file
    parameter:
        path: path to the csv file
        fields: fields
        encoding: encoding format. Default is "utf-8-sig".

    Return Value True for success, false for failure

    """
    try:
        with open(path, 'a', newline='', encoding=encoding) as f:
            writer = csv.writer(f)
            writer.writerow(fields)
        f.close()
        return True
    except Exception as e:
        print(e)
        return False

