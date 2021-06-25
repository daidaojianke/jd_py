#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:18 下午
# @File    : jr_pet_pig.py
# @Project : jd_scripts
# @Desc    : 京东金融->养猪猪
import json
import aiohttp
import asyncio

from urllib.parse import unquote, quote

from utils.notify import notify


class JrPetPig:
    """
    养猪猪
    """
    def __init__(self, pt_pin, pt_key):

        self._cookies = {
            'pt_pin': pt_pin,
            'pt_pet': pt_key
        }
        self._pt_pin = unquote(pt_pin)

    async def run(self):
        pass


def start(pt_pin, pt_key):
    """
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JrPetPig(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())
