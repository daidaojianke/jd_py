#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/29 9:37 上午
# @File    : jr_money_tree_collect.py
# @Project : jd_scripts
# @Desc    : 摇钱树收金果
import asyncio
import aiohttp
from utils.console import println
from jr_money_tree import JrMoneyTree


class JrMoneyTreeCollect(JrMoneyTree):
    """
    金果摇钱树收金果
    """
    def __init__(self, pt_pin, pt_key):
        super(JrMoneyTreeCollect, self).__init__(pt_pin, pt_key)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            is_success = await self.login(session)
            if not is_success:
                println('{}, 登录失败, 退出程序...'.format(self._pt_pin))
            await self.harvest(session)  # 收金果


def start(pt_pin, pt_key, name='金果摇钱树收金果'):
    """
    :param name:
    :param pt_pin:
    :param pt_key:
    :return:
    """
    try:
        app = JrMoneyTreeCollect(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    from utils.process import process_start
    process_start(start, '金果摇钱树收金果')
