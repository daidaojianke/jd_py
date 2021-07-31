#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/27 下午8:28 
# @File    : dj_fruit_collect.py
# @Project : jd_scripts
# @Cron    : 42 */1 * * *
# @Desc    : 到家果园收水滴
import aiohttp
import asyncio
from dj_fruit import DjFruit
from utils.console import println
from utils.process import process_start


class DjFruitCollect(DjFruit):

    def __init__(self, pt_pin, pt_key):
        super(DjFruitCollect, self).__init__(pt_pin, pt_key)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            dj_cookies = await self.login(session)
            if not dj_cookies:
                return
            println('{}, 登录成功...'.format(self.account))

        async with aiohttp.ClientSession(cookies=dj_cookies, headers=self.headers) as session:
            await self.receive_water_wheel(session)  # 领取水车水滴


def start(pt_pin, pt_key, name='到家果园领水滴'):
    """
    程序入口
    """
    try:
        app = DjFruitCollect(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    process_start(start, '到家果园领水滴')
