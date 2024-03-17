# -*- coding: utf-8 -*-

import glob
import numpy as np
import pandas as pd


def count_lines_in_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return len(lines)


def current_file_minbymin_ser(fn):
    yyyymm = fn[-10:-4]
    # 将字符串转换为datetime对象，开始时间为上月最后一天的20:01
    start_date = pd.to_datetime(yyyymm + '01') - pd.DateOffset(hours=4) + pd.DateOffset(minutes=1)
    # 设置结束日期为本月最后一天的20:00
    end_date = start_date + pd.DateOffset(months=1) + pd.offsets.MonthEnd(0) - pd.DateOffset(minutes=1)
    minutely_index = pd.date_range(start=start_date, end=end_date, freq='T').strftime('%Y%m%d%H%M')
    return [int(date) for date in minutely_index]


def split_by_two_digits(s):
    # 检查字符串长度是否为偶数，如果不是，则无法按两个数字切分
    if len(s) % 2 != 0:
        raise ValueError("The string length must be even to split by two digits.")
    else:
        s_add = s.ljust(120, '0')  # 使用 ljust 方法左对齐，用 0 填充到长度 120
        lst = [s_add[i:i + 2] for i in range(0, len(s_add), 2)]  # 拆分成2个字符组成的列表
        # 转换列表中的数字字符串为整数，并将'//'替换为np.nan
        # 使用列表推导式来执行转换，同时处理'//'的情况
        lst_converted = [int(item) if item != '//' else np.nan for item in lst]
        # 将转换后的列表转换为NumPy数组
        num_ser = np.array(lst_converted, dtype=float) / 10  # 使用dtype=float来确保所有元素都是浮点数，包括np.nan
    return num_ser


def read_j_file(j_file):
    min_ser = current_file_minbymin_ser(j_file)
    if count_lines_in_file(j_file) > 10:  # 无缺测情况
        with open(f, 'r') as file:
            # 生成当前文件对应的分钟时间序列
            temp = np.empty([0, 1])  # 生成空矩阵,存储当前txt的数据
            # 开始读取J文件
            line = file.readline()  # 开始读第一行
            line_forward = []
            while line:
                if len(line) > 121:
                    print('line length > 121')
                    break
                line = file.readline().strip()
                line_forward.append(line)
                if line == ',':
                    temp = np.vstack([temp, np.zeros([60, 1])])
                elif line == '/,':
                    temp = np.vstack([temp, np.full([60, 1], np.nan)])
                elif line == '/.' and line_forward[-2][-1] == '.':
                    temp = np.vstack([temp, np.full([60 * 24, 1], np.nan)])
                elif line == '/.' and line_forward[-2][-1] == ',':
                    temp = np.vstack([temp, np.full([60, 1], np.nan)])
                elif line == '/.' and line_forward[-2] == 'R0':
                    temp = np.vstack([temp, np.full([60 * 24, 1], np.nan)])
                elif line == '.' and line_forward[-2] == 'R0':
                    temp = np.vstack([temp, np.zeros([60 * 24, 1])])
                elif line == '.' and line_forward[-2][-1] == '.':
                    temp = np.vstack([temp, np.zeros([60 * 24, 1])])
                elif line == '.' and line_forward[-2][-1] == ',':
                    temp = np.vstack([temp, np.zeros([60, 1])])
                elif len(line) > 1 and line[-1] == ',':
                    min_pre_in_hour = np.array(split_by_two_digits(line.rstrip(','))).reshape(-1, 1)
                    temp = np.vstack([temp, min_pre_in_hour])
                elif len(line) > 1 and line[-1] == '.':
                    min_pre_in_hour = np.array(split_by_two_digits(line.rstrip('.'))).reshape(-1, 1)
                    temp = np.vstack([temp, min_pre_in_hour])
                elif line == '=' and line_forward[-2][-1] == ',':
                    temp = np.vstack([temp, np.zeros([60, 1])])
                elif line == '=' and line_forward[-2][-1] == '.':
                    temp = np.vstack([temp, np.zeros([60 * 24, 1])])
                elif line == '/=' and line_forward[-2][-1] == ',':
                    temp = np.vstack([temp, np.full([60, 1], np.nan)])
                elif line == '/=' and line_forward[-2][-1] == '.':
                    temp = np.vstack([temp, np.full([60 * 24, 1], np.nan)])
                elif len(line) >= 3 and line[-1] == '=':
                    min_pre_in_hour = np.array(split_by_two_digits(line.rstrip('='))).reshape(-1, 1)
                    temp = np.vstack([temp, min_pre_in_hour])
    else:
        temp = np.full_like(min_ser, np.nan, dtype=float)
    if len(temp) == len(min_ser):
        temp = temp.reshape(-1, 1)
    else:
        raise ValueError(f + "读取错误!!!!!!!!!!")  # 抛出异常
    return min_ser, temp


if __name__ == '__main__':
    files = glob.glob(r'f:\JX_Min_Pre\J\*.TXT')
    ##############计算J文件一共有哪些站###########
    sta_id = []
    for f in files:
        sta_id.append(int(f[-16:-11]))
    sta_id_num = set(sta_id)
    #############生成最终存放分钟降水数据的数组###########
    # 设置起始和结束日期
    start_date = '200312312001'
    end_date = '202312312000'
    # 生成时间序列，频率为每分钟
    minutely_index = pd.date_range(start=start_date, end=end_date, freq='T').strftime('%Y%m%d%H%M')
    integer_dates = [int(date) for date in minutely_index]
    pre_min = np.full((len(integer_dates) + 1, 95), np.nan)
    pre_min[1:, 0] = integer_dates
    pre_min[0, 1:] = np.array(list(sta_id_num)).reshape(1, -1)
    np.save(r'F:\JX_Min_Pre\J_pre.npy', pre_min)
    ##############生成最终分钟降水数组###########
    pre_min = np.load(r'f:\JX_Min_Pre\J_pre.npy')
    for f in files:
        print(f)
        time_list, pre = read_j_file(f)
        r_start = np.where(pre_min[:, 0] == time_list[0])[0][0]
        col = np.where(pre_min[0, :] == int(f[-16:-11]))[0][0]
        pre_min[r_start:r_start + len(time_list), col:col + 1] = pre
    np.save(r'F:\JX_Min_Pre\J_pre_20042023.npy', pre_min)
