# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: coarse_ist
# @Author：Uyoin (Yilong Wu) (https://github.com/uyoin),Ryan Zhang (https://github.com/hz157)
# @DateTime: 3/3/2023 上午10:31


import spacy
import src.unit.status
import pandas as pd
import jionlp as jio
from src.config import config
from datetime import datetime
from src.data.csv import write_csv
from src.api.baidu import Geocoder_v3_search_stloc
from src.data.standardize import time_standardize, space_standardize

spacy.require_gpu()  # 使用GPU请取消该行注释
NER = spacy.load("zh_core_web_trf",
                 exclude=["tagger", "parser", "entity_linker", "entity_ruler", "textcat", "textcat_multilabel",
                          "lemmatizer", "trainable_lemmatizer", "morphologizer", "attribute_ruler", "senter",
                          "sentencizer", "tok2vec"])  # 排除部分无关标签，提升效率


def flatten_list(write_data):
    """
        用于flatten输入的列表
    Args:
        write_data: 待flatten的列表

    Returns:    list_need：flatten后的列表

    """
    global global_var
    list_need = []
    for item in write_data:
        if isinstance(item, list):  # 如果当前元素是列表，递归调用flatten_list函数
            flatten_list(item)
        else:  # 否则将当前元素添加到全局变量中
            list_need.append(item)
    return list_need


def sentence_split(text, cri):
    """
        文本分句， 采用jionlp.split_sentence
        https://github.com/dongrixinyu/JioNLP/wiki/Gadget-%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3#user-content-%E6%96%87%E6%9C%AC%E5%88%86%E5%8F%A5
    Args:
        text: 文本列表
        cri: 粒度 分为 coarse粗粒度 和 fine细粒度

    Returns: 文本结果 list

    """
    try:
        sentence = jio.split_sentence(text, criterion=cri)  # jionlp 文本分句
        return sentence
    except Exception as e:
        print(e)
        return None


def create_write_data(native_data, sentence, label_info):
    """
        构造中间结果列表，用于后续导出csv观察和检查粗粒度提取的中间结果
    Args:
        native_data: 爬取的原数据字典
        sentence: jionlp 拆分的句子
        label_info：该句NER提取的所有标签信息字典

    Returns: result：中间结果列表

    """
    result = [[]] * 14
    check = [[]] * 14
    if 'FAC' in label_info.keys():  # 判断是否有空间信息，无则弃之
        result[0] = native_data['text']  # 原始文本
        result[1] = sentence  # jionlp 拆分的句子
        result[2] = native_data['create_at']  # 博文时间
        TIME = []
        if 'DATE' in label_info.keys():  # 判断是否有DATE标签
            TIME = label_info['DATE']
        if 'TIME' in label_info.keys():
            TIME = TIME + label_info['TIME']  # spacy 时间
        result[3] = TIME  # spacy 时间
        if len(label_info['GPE']) > 0:
            result[4] = label_info['GPE']  # spacy 行政区
        elif native_data['region'] != "":
            result[4] = native_data['region']
        else:
            result[4] = ''
        if label_info['FAC'] in config.FAC_REVERSE_KEYWORD:  # 设施反向关键字 修改config/config.py
            result[5] = ''  # 反向关键字排除，添加空数据
        else:
            result[5] = label_info['FAC']  # spacy 设施

        if 'TIME' in label_info.keys() or 'DATE' in label_info.keys():  # 判断是否有时间标签信息，无则直接使用创建时间
            ner_time, ner_time_status = time_standardize(TIME,
                                                             native_data['create_at'])  # 时间标准化
            result[6] = ner_time  # 追加ner时间数据
            result[7] = ner_time_status  # 追加ner时间状态
        else:
            result[6] = result[2].split(" ")[0]
            result[7] = src.unit.status.TimeStandardStatus.unrecognized.value
        ner_spacy, ner_spacy_status = space_standardize(label_info, native_data)  # 空间标准化
        result[8] = ner_spacy
        result[9] = ner_spacy_status
        loc_wgs84, confidence = Geocoder_v3_search_stloc(ner_spacy, ner_spacy_status)
        result[10] = loc_wgs84
        result[11] = confidence
        result[12] = str(native_data['mid']) + '\t'

    if check == result:
        return None
    return result


def NER_Standardize_Geocoder(i, sentence):
    """
        实现NER、时空标准化、地理编码
        NER部分采用spacy， 包: zh_core_web_trf, python -m spacy download zh_core_web_trf
    Args:
        i:爬取的原数据字典
        sentence: 经过jionlp分句的列表 list

    Returns: 标签信息和数据 dict

    """
    if sentence is None:
        return

    # 一些初始化
    current = 0
    result = {}
    location = []
    star_time = datetime.now()
    error_dict = {
        30: 5000,
        40: 2000,
        50: 1000,
        60: 500,
        70: 300,
        75: 200,
        80: 100,
        90: 50,
        100: 20,
    }

    for sentence_num in range(len(sentence)):  # 遍历jionlp分句的列表
        result.clear()
        t1 = datetime.now()  # 开始时间
        sub_sentence = sentence[sentence_num]  # 分句后的子句
        NER.max_length = len(max(sub_sentence, key=len))  # 自定义max_length为该句的字符长度，减少内存占用
        pipe = NER.pipe(sub_sentence, batch_size=1024)  # 对分句后的子句进行NER，batch_size可根据运行设备显存来设定

        GPE = []
        for text in pipe:
            result.clear()
            # 没标签就拜拜
            if len(text.ents) == 0 or text.ents == '……':
                continue

            # 获取这句话的所有标签
            for ent in text.ents:
                if ent.label_ in result.keys():  # 之前已写入该标签
                    value = result[ent.label_]  # 获取之前写入的数据
                    value.append(ent.text)  # 追加新的数据
                    result[ent.label_] = value  # 重新赋值
                else:  # 之前未写入该标签
                    result[ent.label_] = [ent.text]  # 赋值

            # 对于整段话需要进行GPE的暂时固化并覆盖，否则下一句即使有FAC，也无法连接组合
            if "GPE" in result:
                for gpe in result['GPE']:
                    GPE.append(gpe)
            result['GPE'] = list(set(GPE))

            write_data = create_write_data(i[current], text, result) # ※时空标准化、地理编码在这里面
            if not write_data:
                continue

            write_csv(config.SAVE_PATH, write_data)  # 追加CSV数据

            # 若有地理编码后的坐标且大于等于30的置信度就保留，同时计算置信度相对应的缓冲区大小（百度地图标准）
            if isinstance(write_data[10], str):
                if write_data[10] == "Nodata" or write_data[11] == "Nodata":
                    continue
            elif isinstance(write_data[10], list):
                for x, y, z, c in zip(write_data[8], write_data[10], write_data[11], write_data[9]):
                    if isinstance(write_data[6], list):
                        time = write_data[6][0]
                        time_status = write_data[7][0]
                    elif isinstance(write_data[6], str):
                        time = write_data[6]
                        time_status = write_data[7]
                    stdloc_status = c
                    std_loc = x
                    if y == "Nodata" or z == "Nodata":
                        continue
                    if isinstance(y, dict):
                        continue
                    WGS84 = y.split(",")
                    lon = WGS84[0]
                    lat = WGS84[1]
                    confidence = int(z.split("  ")[0])
                    if confidence >= 30:
                        # 根据confidence值从字典中获取解析误差绝对精度的阈值
                        for threshold in error_dict:
                            if confidence == threshold:
                                error_threshold = error_dict[threshold]
                                break
                        else:
                            error_threshold = 5000  # 如果字典中没有匹配的值，将误差范围设为5000米
                        location.append(
                            [write_data[12], time, time_status, std_loc, stdloc_status, lon, lat, confidence,
                             error_threshold])

        current += 1
        t2 = datetime.now()  # 结束时间
        print(f'当前执行: {current} / 总数据: {len(sentence)} 单条耗时: {str(t2 - t1)}')  # 状态显示
        # if current > 1000:
        #     break

    # 导出粗粒度标准化表为xlsx文件
    df = pd.DataFrame(location)
    df.to_excel('data1.xlsx', index=False)

    end_time = datetime.now()
    sum_time = end_time - star_time
    print('总处理时间耗时:%s,共%i条微博,平均每条耗时:%s' % (sum_time, current, sum_time / current))


def coarse_ist(data):
    # 文本分句
    sentence_list = []
    for i in range(len(data)):
        sentence_list.append(sentence_split(data[i]['text'], cri='coarse'))
    # 一次性实现NER、时空标准化、地理编码
    NER_Standardize_Geocoder(data, sentence_list)
