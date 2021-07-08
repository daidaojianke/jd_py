#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/8 11:37 上午
# @File    : jd_small_home.py
# @Project : jd_scripts
# @Desc    : 东东小窝, 活动地址: https://h5.m.jd.com/babelDiy/Zeus/2HFSytEAN99VPmMGZ6V4EYWus1x/index.html
import aiohttp
import asyncio

from urllib.parse import unquote, quote

from config import USER_AGENT


class JdSmallHome:
    """
    东东小窝
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
        self._pt_pin = unquote(pt_pin)

    async def login(self):
        """
        :return:
        """
