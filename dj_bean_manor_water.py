#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/28 5:58 下午
# @File    : dj_bean_manor_water.py
# @Project : jd_scripts
# @Desc    : 京东到家鲜豆庄园领水浇水
import asyncio
import aiohttp

from dj_bean_manor import DjBeanManor
from utils.process import process_start
from utils.console import println


class DjBeanManorWater(DjBeanManor):

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        super(DjBeanManorWater, self).__init__(pt_pin, pt_key)

    async def run(self):
        """
        程序入口
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            dj_cookies = await self.login(session)
            if not dj_cookies:
                return
            println('{}, 登录成功...'.format(self.account))

        async with aiohttp.ClientSession(cookies=dj_cookies, headers=self.headers) as session:
            activity_info = await self.get_activity_info(session)
            if not activity_info:
                println('{}, 获取活动ID失败, 退出程序!'.format(self.account))
                return
            await self.collect_watter(session)
            await self.watering(session)


def start(pt_pin, pt_key, name='鲜豆庄园领水/浇水'):
    """
    程序入口
    :param name:
    :param pt_pin:
    :param pt_key:
    :return:
    """
    try:
        app = DjBeanManorWater(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    process_start(start, '鲜豆庄园领水/浇水')
