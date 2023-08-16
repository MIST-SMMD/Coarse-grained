# Copyright (c) 2023.
# !/usr/bin/python
# -*- coding: UTF-8 -*-
# @Project: mist
# @FileName: coarse_ist_process
# @Author：Uyoin (Yilong Wu) (https://github.com/uyoin),Ryan Zhang (https://github.com/hz157)
# @DateTime: 3/3/2023 上午10:31


import spacy
import src.config.status
import pandas as pd
from src.config import config
from datetime import datetime
from jionlp import split_sentence
from src.data.csv import write_csv
from src.coarse_ist_process.baidu import Geocoder_v3_search_stloc
from src.coarse_ist_process.standardize import time_standardize, space_standardize

def flatten_list(write_data):
    """
        List for flatten input
    Args.
        write_data: list to be flattened

    Returns: list_need: list after flatten

    """
    global global_var
    list_need = []
    for item in write_data:
        if isinstance(item, list): # If the current element is a list, recursively call flatten_list function
            flatten_list(item)
        else: # Otherwise add the current element to the global variable
            list_need.append(item)
    return list_need


def sentence_split(text, cri):
    """
        Text Split Sentence, using jionlp.split_sentence
        https://github.com/dongrixinyu/JioNLP/wiki/Gadget-%E8%AF%B4%E6%98%8E%E6%96%87%E6%A1%A3#user-content-%E6%96%87%E6%9C%AC%E5%88%86% E5%8F%A5
    Args.
        text: text list
        cri: granularity, coarse and fine.

    Returns: text result list

    """
    try:
        sentence = split_sentence(text, criterion=cri)  # jionlp text clauses
        return sentence
    except Exception as e:
        print(e)
        return None


def create_write_data(native_data, sentence, label_info):
    """
        Constructs a list of intermediate results for subsequent exporting of csv observations and checking intermediate results of coarse-grained extraction
    Args.
        native_data: the crawled native data dictionary
        sentence: sentence split by jionlp
        label_info: dictionary of all labels extracted from this sentence.

    Returns: result: list of intermediate results

    """
    result = [[]] * 14
    check = [[]] * 14
    if 'FAC' in label_info.keys(): # Determine if there is spatial information, discard if there is none
        result[0] = native_data['text'] # raw text
        result[1] = sentence # sentence split by jionlp
        result[2] = native_data['create_at'] # time of the blog post
        TIME = []
        if 'DATE' in label_info.keys(): # determine if there is a DATE label
            TIME = label_info['DATE'] # blog post time
        if 'TIME' in label_info.keys(): # Determine if there is a DATE label TIME = label_info['DATE'].
            TIME = TIME + label_info['TIME'] # spacy time
        result[3] = TIME # spacy time
        if len(label_info['GPE']) > 0:
            result[4] = label_info['GPE'] # spacy administrative district
        elif native_data['region'] ! = "":
            result[4] = native_data['region'] # spacy Administrative regions
        else:
            result[4] = ''
        if label_info['FAC'] in config.FAC_REVERSE_KEYWORD: # facility reverse keyword modify config/config.py
            result[5] = '' # reverse keyword exclusion, add empty data
        else:
            result[5] = label_info['FAC'] # spacy facility

        if 'TIME' in label_info.keys() or 'DATE' in label_info.keys(): # Determine if there is timestamp information, if not then directly use creation time
            ner_time, ner_time_status = time_standardize(TIME,
                                                             native_data['create_at']) # time standardization
            result[6] = ner_time # append ner time data
            result[7] = ner_time_status # Append ner time status
        else:
            result[6] = result[2].split(" ")[0]
            result[7] = src.config.status.TimeStandardStatus.unrecognized.value
        ner_spacy, ner_spacy_status = space_standardize(label_info, native_data) # space standardization
        result[8] = ner_spacy
        result[9] = ner_spacy_status
        loc_wgs84, confidence = Geocoder_v3_search_stloc(ner_spacy, ner_spacy_status)
        result[10] = loc_wgs84
        result[11] = confidence
        result[12] = str(native_data['mid']) + '\t'

    if check == result:
        return None
    return result


def NER_Standardize_Geocoder(i, sentence,NER):
    """
        Implementing NER, spatio-temporal normalization, geocoding
        NER partially using spacy, package: zh_core_web_trf, python -m spacy download zh_core_web_trf
    Args.
        Args: i: the original data dictionary to be crawled.
        sentence: list after jionlp clause list

    Returns: tag information and data dict

    """
    if sentence is None:
        return

    current = 0
    result = {}
    location = []
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
    print(f'Total data volume: {len(sentence)} ')
    star_time = datetime.now()
    for sentence_num in range(len(sentence)): # iterate through the list of jionlp clauses
        result.clear()
        t1 = datetime.now() # start time
        sub_sentence = sentence[sentence_num] # sub-sentence after clause
        NER.max_length = len(max(sub_sentence, key=len)) # Customize max_length to be the character length of the sentence to reduce memory usage
        pipe = NER.pipe(sub_sentence, batch_size=1024) # NER the clause after the split, batch_size can be set according to the running device memory

        GPE = []
        for text in pipe:
            result.clear()
            if len(text.ents) == 0 or text.ents == '……':
                continue

            # Get all the tags for this sentence
            for ent in text.ents: # previously written to this label
                if ent.label_ in result.keys(): # previously written to this label
                    value = result[ent.label_] # Get the previously written data
                    value.append(ent.text) # append new data
                    result[ent.label_] = value # reassign the value
                else: # The label was not written before
                    result[ent.label_] = [ent.text] # assign value

            # Temporary curing and overwriting of GPE is required for the entire sentence, otherwise the next sentence cannot connect the combination even if it has a FAC
            if "GPE" in result:
                for gpe in result['GPE']:
                    GPE.append(gpe)
            result['GPE'] = list(set(GPE))

            write_data = create_write_data(i[current], text, result) # ※Time standardization, geocoding is in here 
            if not write_data:
                continue

            write_csv(config.TEMP_SAVE_PATH, write_data)

            # If there are geocoded coordinates with a confidence level greater than or equal to 30, retain them and calculate the buffer size corresponding to the confidence level (Baidu map standard)
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
                        # Threshold for absolute precision of parsing error from dictionary based on CONFIDENCE value
                        for threshold in error_dict:
                            if confidence == threshold:
                                error_threshold = error_dict[threshold]
                                break
                        else:
                            error_threshold = 5000  # If there is no matching value in the dictionary, set the margin of error to 5000 meters
                        location.append(
                            [write_data[12], time, time_status, std_loc, stdloc_status, lon, lat, confidence,
                             error_threshold])

        current += 1
        t2 = datetime.now()
        print(f'Currently executing: {current} / {len(sentence)} | Single text processing time: {str(t2 - t1)}')

    df = pd.DataFrame(location,columns=["mid","date","time_status","ts_loc","space_status","X_WGS84","Y_WGS84","confidence","buffer"])
    df.to_excel(config.RESULT_SAVE_PATH, index=False)

    end_time = datetime.now()
    sum_time = end_time - star_time
    print('Total processing time elapsed:%s,Total %i tweets,Average time spent per text:%s' % (sum_time, current, sum_time / current))


def coarse_ist(data,devices:str):
    if devices.upper() == "GPU":
        spacy.require_gpu()  
        print("GPU is enabled and ready for NER")
    elif devices.upper() == "CPU":
        print("CPU is enabled and ready for NER")
    else:
        print("Please use the correct device: GPU or CPU !")

    NER = spacy.load("zh_core_web_trf",
                     exclude=["tagger", "parser", "entity_linker", "entity_ruler", "textcat", "textcat_multilabel",
                              "lemmatizer", "trainable_lemmatizer", "morphologizer", "attribute_ruler", "senter",
                              "sentencizer", "tok2vec"])  

    sentence_list = []
    for i in range(len(data)):
        sentence_list.append(sentence_split(data[i]['text'], cri='coarse'))
    NER_Standardize_Geocoder(data, sentence_list,NER)
