#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/24 19:43
# @File    : jd_earn_bean.py
# @Project : jd_scripts
# @Desc    : 赚京豆(微信小程序)-赚京豆-签到领京豆
import asyncio
import time
import urllib.parse

import aiohttp
import json

from urllib.parse import unquote, quote

from config import USER_AGENT

from utils.notify import notify
from utils.logger import logger
from utils.console import println
from utils.process import process_start


class JdEarnBean:
    """
    微信小程序 赚京豆
    """
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'jdmall;android;version/10.0.4;build/88641;os/11;'
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._pt_pin = unquote(pt_pin)

    async def run(self):
        """
        程序入口
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            pass


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdEarnBean(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())
    # process_start(start, '赚京豆')
