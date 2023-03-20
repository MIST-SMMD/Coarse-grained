from config import config
from data.csv import read_csv, write_csv
from data.excel import read_excel, write_excel
from data.ner import sentence_split, spacy_label_mark, create_write_data,ner


def read_weibo(path, fileType):
    """
        微博数据集的读取
    Args:
        path: 文件路径
        fileType: 文件类型

    Returns:数据列表list

    """
    if fileType.lower() == "excel":
        dataSetData = read_excel(path)
    elif fileType.lower() == "csv":
        dataSetData = read_csv(path, 'ansi')
    else:
        print("请输入正确的类型，仅支持csv与excel文件格式！")
    result = []
    for item in dataSetData:
        result.append({'create_at': str(item[1]), 'text': str(item[2]), 'region': str(item[4])})  # 构造list
    return result


if __name__ == '__main__':
    # fields = ['text', 'sentence', 'create_at', 'ner_time', 'ner_gpe', 'ner_fac', 'stand_time', 'stand_time_status',
    #           'stand_loc', 'stand_loc_status', 'lng-bd09', 'lat-bd09', 'lng-wgs84', 'lat-wgs84', 'street_id']  # 列名
    fields = ['text', 'sentence', 'create_at', 'ner_time', 'ner_gpe', 'ner_fac', 'stand_time', 'stand_time_status',
              'stand_loc', 'stand_loc_status', 'loc_bd09', 'loc_wgs84', 'street_id']  # 列名
    write_csv(config.SAVE_PATH, fields)  # 写标签列   验证csv可能会导致mid错乱，弃用csv
    # write_excel(config.SAVE_PATH, fields)   # 写标签列
    data = read_weibo(config.ORIGINAL_PATH, fileType="excel")  # 读取数据库导出的EXCEL数据
    ner(data)


