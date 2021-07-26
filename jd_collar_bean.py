#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/26 9:55 上午
# @File    : jd_collar_bean.py
# @Project : jd_scripts
# @Desc    : 京东APP->领金豆


class JdCollarBean:
    """
    领金豆
    """
    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
