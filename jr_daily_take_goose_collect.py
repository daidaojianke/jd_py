#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/29 9:29 上午
# @File    : jr_daily_take_goose_collect.py.py
# @Project : jd_scripts
# @Cron    : 5 */1 * * *
# @Desc    : 天天提额收鹅蛋
import asyncio
import aiohttp
from utils.console import println

from jr_daily_take_goose import JrDailyTakeGoose


class JrDailyTakeGooseCollect(JrDailyTakeGoose):
    """
    天天提额收鹅蛋
    """
    async def run(self):
        """
        程序入口
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            await self.to_withdraw(session)


def start(pt_pin, pt_key, name='天天提鹅收鹅蛋'):
    """
    程序入口
    :param name:
    :param pt_pin:
    :param pt_key:
    :return:
    """
    try:
        app = JrDailyTakeGooseCollect(pt_pin, pt_key)
        asyncio.run(app.run())
        return app.message
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    from utils.process import process_start
    process_start(JrDailyTakeGooseCollect, '天天提鹅收鹅蛋')
