from src.config import config
from src.data.csv import read_csv, write_csv
from src.data.excel import read_excel
from src.coarse_ist import coarse_ist


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
        result.append(
            {'create_at': str(item[1]), 'text': str(item[2]), 'region': str(item[4]), 'mid': str(item[0])})  # 构造list
    return result


if __name__ == '__main__':
    fields = ['text', 'sentence', 'create_at', 'ner_time', 'ner_gpe', 'ner_fac', 'stand_time', 'stand_time_status',
              'stand_loc', 'stand_loc_status', 'loc_wgs84', 'loc_confidence', 'mid']  # 列名
    write_csv(config.SAVE_PATH, fields)  # 写标签列
    # write_excel(config.SAVE_PATH, fields)   # 写标签列
    data = read_weibo(config.ORIGINAL_PATH, fileType="excel")  # 读取数据库导出的EXCEL数据
    coarse_ist(data)  # 粗粒度时空信息提取
