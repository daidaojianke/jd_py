#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/28 5:53 下午
# @File    : test.py
# @Project : jd_scripts
# @Desc    :
from utils.image import detect_displacement
from config import IMAGES_DIR
import os

if __name__ == '__main__':
    test = [
        '0a74407df5df4fa99672a037eec61f7e@dbb21614667246fabcfd9685b6f448f3@6fbd26cc27ac44d6a7fed34092453f77'
        '@61ff5c624949454aa88561f2cd721bf6@56db8e7bc5874668ba7d5195230d067a@b9d287c974cc498d94112f1b064cf934'
        '@23b49f5a106b4d61b2ea505d5a4e1056@8107cad4b82847a698ca7d7de9115f36',
        'b1638a774d054a05a30a17d3b4d364b8@f92cb56c6a1349f5a35f0372aa041ea0@9c52670d52ad4e1a812f894563c746ea'
        '@8175509d82504e96828afc8b1bbb9cb3@2673c3777d4443829b2a635059953a28@d2d5d435675544679413cb9145577e0f',
    ]

    for i in test:
        for j in i.split('@'):
            print('-', j)