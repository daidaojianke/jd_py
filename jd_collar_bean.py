#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/26 9:55 上午
# @File    : jd_collar_bean.py
# @Project : jd_scripts
# @Desc    : 京东APP->领金豆
import asyncio
import aiohttp
from urllib.parse import unquote


class JdCollarBean:
    """
    领金豆
    """
    def __init__(self, pt_pin, pt_key, **kwargs):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._account = unquote(pt_pin)
        self._queue = kwargs.get('queue', None)

    @property
    def message(self):
        return 'hello world'

    async def request(self):
        """
        请求数据
        :return:
        """
        pass

    async def run(self):
        """
        入口
        :return:
        """
        await asyncio.sleep(10)


def start(pt_pin, pt_key):
    """
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdCollarBean(pt_pin, pt_key)
    asyncio.run(app.run())
    return app.message


if __name__ == '__main__':
    from utils.process import process_start
    process_start(start, '领京豆')
