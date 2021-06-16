#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/14 15:12
# @File    : logger.py
# @Project : jd_scripts
import os
from loguru import logger
from config import LOG_DIR


def get_logger(log_name=None):
    """
    获取日志实例
    :return:
    """
    if not log_name:
        log_name = __name__

    log_path = LOG_DIR + '/' + log_name + '.log'

    logger.remove()
    logger.add(log_path, level='INFO', rotation='00:00', retention="3 days", compression="zip",
               format="[{time:YYYY-MM-DD HH:mm:ss}] | {level} | {message}",
               encoding="utf-8", enqueue=True)

    return logger
