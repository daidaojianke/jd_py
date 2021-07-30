#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/29 9:41 上午
# @File    : jd_factory_collect.py
# @Project : jd_scripts
# @Desc    : 东东工厂收电量
import asyncio
import aiohttp

from jd_factory import JdFactory
from utils.console import println
from utils.process import process_start


class JdFactoryCollect(JdFactory):
    """
    东东工厂收电量
    """
    def __init__(self, pt_pin, pt_key):
        super(JdFactoryCollect, self).__init__(pt_pin, pt_key)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            is_success = await self.init(session)
            if not is_success:
                println('{}, 无法初始化数据, 退出程序!'.format(self._pt_pin))
                return
            await self.collect_electricity(session)


def start(pt_pin, pt_key, name='东东工厂-收电量'):
    """
    :param name:
    :param pt_pin:
    :param pt_key:
    :return:
    """
    try:
        app = JdFactoryCollect(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    process_start(start, '东东工厂-收电量')