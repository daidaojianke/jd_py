#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 2:01 下午
# @File    : clean_log.py
# @Project : jd_scripts
# @Desc    : 清除日志脚本
import re
import os
import moment
from config import LOG_DIR
from utils.console import println


def clean_log():
    """
    清除日志脚本, 仅保留当天的日志
    :return:
    """
    count = 0
    today_date = moment.now().format('YYYY-M-D')
    for file in os.listdir(LOG_DIR):
        if not os.path.isfile(file):  # 跳过文件夹
            continue
        if os.path.splitext(file)[-1] != '.log':   # 跳过非日志文件
            continue
        try:
            date = re.split(r'\.|_', file)[-2]
            if date == today_date:  # 跳过当天的记录
                continue
            os.remove(os.path.join(LOG_DIR, file))
            count += 1
        except Exception as e:
            println(e.args)
    println('成功清除个{}日志文件!'.format(count))


if __name__ == '__main__':
    clean_log()
