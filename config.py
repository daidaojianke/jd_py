#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/16 11:31 上午
# @File    : config.py
# @Project : jd_scripts
# @Desc    : 脚本配置文件
import os
import re


# 环境变量中读取JD_COOKIES.
JD_COOKIES = [{'pt_pin': re.findall('pt_pin=(.*?);', i).pop() if re.match('pt_pin=(.*?);', i) is not None else '',
               'pt_key': re.findall('pt_key=(.*?);', i).pop() if re.findall('pt_key=(.*?);', i) is not None else ''}
              for i in os.getenv('JD_COOKIES', '').split('&') if
              re.match('pt_pin=(.*?);pt_key=(.*?);', i) is not None] + [
    # 配置COOKIES
    {
        "pt_pin": "",
        "pt_key": ""
    },
    # 配置COOKIES
]

JD_COOKIES = [i for i in JD_COOKIES if 'pt_pin' in i and 'pt_key' in i and i['pt_pin'] and i['pt_key']]
