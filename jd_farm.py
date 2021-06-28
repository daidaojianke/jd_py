#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:27 下午
# @File    : jd_farm.py
# @Project : jd_scripts
# @Desc    : 京东APP-东东农场
import asyncio
import aiohttp
import json

from urllib.parse import unquote, quote
from utils.console import println
from config import USER_AGENT


class JdFarm:
    """
    京东农场
    """
    headers = {
        'user-agent': USER_AGENT,
        'content-type': 'application/json',
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._pt_pin = unquote(pt_pin)
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._farm_info = None

    async def request(self, session, function_id, body=None):
        """
        :param session:
        :param body:
        :param function_id:
        :return:
        """
        try:
            if not body:
                body = dict()
            body['version'] = 13
            body['channel'] = 1

            url = 'https://api.m.jd.com/client.action?functionId={}&appid=wh5&{}'.format(function_id, quote(json.dumps(body)))
            println(url)
            response = await session.get(url=url)
            data = await response.json()
            return data
        except Exception as e:
            println('{}, 获取服务器数据错误:{}'.format(self._pt_pin, e.args))

    async def init_for_farm(self, session):
        """
        初始化农场数据
        :param session:
        :return:
        """
        data = await self.request(session, 'initForFarm')
        if data['code'] != '0' or 'farmUserPro' not in data:
            return None
        return data['farmUserPro']

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            self._farm_info = await self.init_for_farm(session=session)
            if not self._farm_info:
                println('{}, 无法获取农场数据, 退出程序!'.format(self._pt_pin))
                return
            println(self._farm_info)


def start(pt_pin, pt_key):

    app = JdFarm(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())
