#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/25 下午8:45 
# @File    : jd_joy_feed.py
# @Project : jd_scripts 
# @Desc    : 宠汪汪喂狗
import aiohttp
import ujson
import asyncio
from jd_joy import JdJoy
from utils.console import println


class JdJoyFeed(JdJoy):
    """
    宠汪汪喂狗
    """
    """
    宠汪汪兑换京豆
    """
    def __init__(self, pt_pin, pt_key):
        super(JdJoyFeed, self).__init__(pt_pin, pt_key)

    async def feed_food(self, session, feed_count=80):
        """
        喂狗, 默认80g
        """
        path = 'pet/feed'
        params = {
            'feedCount': feed_count
        }
        data = await self.request(session, path, params)
        if data and data['errorCode'] and 'ok' in data['errorCode']:
            println('{}, 成功喂狗一次, 消耗狗粮:{}!'.format(self._pt_pin, feed_count))
        else:
            println('{}, 喂狗失败!'.format(self._pt_pin))

    async def run(self):
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._aiohttp_cookies,
                                         json_serialize=ujson.dumps) as session:
            await self.feed_food(session)


def start(pt_pin, pt_key):
    """
    宠汪汪商品兑换
    """
    app = JdJoyFeed(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from utils.process import process_start
    process_start(start, '宠汪汪喂狗')
