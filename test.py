#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/28 5:53 下午
# @File    : test.py
# @Project : jd_scripts
# @Desc    :
from utils.image import detect_displacement

if __name__ == '__main__':
    res = detect_displacement('./slider.png', './bg.png')
    print(res)