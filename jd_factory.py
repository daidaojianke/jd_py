#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:27 下午
# @File    : jd_factory.py
# @Project : jd_scripts
# @Desc    : 京东APP->东东工厂
import asyncio
import aiohttp
import json
import time
from urllib.parse import unquote, quote

from utils.console import println
from utils.notify import notify
from utils.process import process_start

from config import USER_AGENT, JD_FACTORY_SHARE_CODE


class JdFactory:

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://h5.m.jd.com',
    }

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
        self._host = 'https://api.m.jd.com/client.action/'

    async def request(self, session, function_id=None, params=None,  method='post'):
        """
        :param params:
        :param function_id:
        :param session:
        :param method:
        :return:
        """
        if params is None:
            params = {}
        try:
            session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
            url = self._host + '?functionId={}&body={}&client=wh5&clientVersion=1.0.0'.format(function_id, quote(json.dumps(params)))
            if method == 'post':
                response = await session.post(url=url)
            else:
                response = await session.get(url=url)

            text = await response.text()

            data = json.loads(text)

            return data
        except Exception as e:
            println('{}, 请求服务器数据失败, {}'.format(self._pt_pin, e.args))

    async def choose_product(self, session):
        """
        选择商品
        :param session:
        :return:
        """

    async def init(self, session):
        """
        获取首页数据
        :param session:
        :return:
        """
        data = await self.request(session, 'jdfactory_getHomeData', {})
        if data['code'] != 0 or data['data']['bizCode'] != 0:
            println('{}, 无法获取活动数据!'.format(self._pt_pin))
            return False
        data = data['data']['result']

        have_product = data['haveProduct']  # 是否有生产的商品
        new_user = data['newUser']   # 是否新用户

        if new_user == 1 and have_product == 2:
            println('{}, 此账号为新用户暂未开启活动, 现在为您从库存种选择商品!\n'.format(self._pt_pin))
            await self.choose_product(session)

        if new_user == 0 and have_product == 2:
            println('{}, 此账号未选购商品, 但可以做任务!'.format(self._pt_pin))

    async def help_friend(self, session):

        for code in JD_FACTORY_SHARE_CODE:
            params = {
                "taskToken": code,
            }
            data = await self.request(session, 'jdfactory_collectScore', params)
            println('{}, 助力好友{}, {}'.format(self._pt_pin, code, data['data']['bizMsg']))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            #await self.init(session)
            await self.help_friend(session)


def start(pt_pin, pt_key):
    """
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdFactory(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())