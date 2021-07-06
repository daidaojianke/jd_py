#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:21 下午
# @File    : jd_cute_pet.py
# @Project : jd_scripts
# @Desc    : 京东APP->我的->东东萌宠
import aiohttp
import asyncio

from urllib.parse import unquote


class JdCutePet:
    """
    东东萌宠
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

    async def request(self, session, function_id, body=None):
        if body is None:
            body = {}


    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession() as session:
            pass


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdCutePet(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())