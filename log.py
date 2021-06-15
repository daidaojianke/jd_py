#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/14 15:12
# @File    : log.py
# @Project : jd_scripts
import sys
import os
from loguru import logger
from rich.logging import RichHandler

LOG_DIR = os.getenv('LOG_DIR', 'logs')


def get_logger(log_name=None):
    """
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
