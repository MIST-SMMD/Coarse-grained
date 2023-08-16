from src.config import config
from src.data.excel import read_excel
from src.coarse_ist import coarse_ist
from src.data.csv import read_csv, write_csv

def read_weibo(path, fileType):
    """
        Reading of the microblogging dataset
    Args.
        path: file path
        fileType: file type

    Returns: data list list

    """
    if fileType.lower() == "excel":
        dataSetData = read_excel(path)
    elif fileType.lower() == "csv":
        dataSetData = read_csv(path, 'ansi')
    else:
        print("Please enter the correct type to support csv & excel file formats only!")
    result = []
    for item in dataSetData:
        result.append(
            {'create_at': str(item[1]), 'text': str(item[2]), 'region': str(item[4]), 'mid': str(item[0])})  # Build list
    return result


if __name__ == '__main__':
    fields = ['text', 'sentence', 'create_at', 'ner_time', 'ner_gpe', 'ner_fac', 'stand_time', 'stand_time_status',
              'stand_loc', 'stand_loc_status', 'loc_wgs84', 'loc_confidence', 'mid'] 
    write_csv(config.TEMP_SAVE_PATH, fields)  # Write Label Column
    data = read_weibo(config.ORIGINAL_PATH, fileType="excel")  # Read EXCEL data exported from database
    coarse_ist(data[:50],devices="CPU")  # Coarse-grained spatio-temporal information extraction (here the default CPU and the first hundred are demonstrated)
