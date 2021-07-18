#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:24 下午
# @File    : jx_farm.py
# @Project : jd_scripts
# @Desc    : 京喜APP->京喜农场


class JxFactory:

    def __init__(self, pt_pin, pt_key):

        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }

    async def run(self):
        """
        """