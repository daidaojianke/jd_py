#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/25 下午8:45 
# @File    : jd_joy_feed.py
# @Project : jd_scripts
# @Cron    : 10 */3 * * *
# @Desc    : 宠汪汪喂狗
import aiohttp
import ujson
import asyncio
from utils.logger import logger
from jd_joy import JdJoy
from utils.console import println


class JdJoyFeed(JdJoy):
    """
    宠汪汪喂狗
    """

    @logger.catch
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

        await self.close_browser()


def start(pt_pin, pt_key, name='宠汪汪喂食'):
    """
    宠汪汪商品兑换
    """
    try:
        app = JdJoyFeed(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    from utils.process import process_start
    from config import JOY_PROCESS_NUM
    process_start(start, '宠汪汪喂狗', process_num=JOY_PROCESS_NUM)
