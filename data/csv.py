# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: csv
# @Description: CSV 文件操作
# @Author：Ryan Zhang    (https://github.com/hz157)
# @DateTime: 3/3/2023 上午10:31


"""
    CSV文件读写操作
"""

import os
import csv


def read_csv(path, encoding: str = 'utf-8'):
    """
        读取CSV文件
    Args:
        path: csv文件路径
        encoding: 编码格式. Defaults to 'utf-8'.

    Returns:list or None

    """
    result = []
    if os.path.exists(path):  # 判断CSV是否存在
        with open(path, 'r', encoding=encoding) as f:
            lines = csv.reader(f)
            next(lines)
            for line in lines:
                result.append(line)
        return result
    else:  # 不存在返回空值
        return None


def write_csv(path, fields, encoding: str = 'utf-8-sig'):
    """
        写入CSV文件
    Args:
        path: csv文件路径
        fields: 字段
        encoding: 编码格式. Defaults to 'utf-8-sig'.

    Returns: True Success, False Fail

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

