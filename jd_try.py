#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/3 10:53
# @File    : jd_try.py
# @Project : jd_scripts
# @Cron    : #0 10 * * *
# @Desc    : 京东试用

class JdTry:

    def __init__(self, pt_pin, pt_key):
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._pt_pin = pt_pin

    async def request(self, session, url, method):
        """
        请求数据
        """
        pass

    async def run(self):
        """
        :return:
        """
        pass

