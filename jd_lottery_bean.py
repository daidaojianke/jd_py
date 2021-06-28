#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/28 9:35 上午
# @File    : jd_lottery_bean.py
# @Project : jd_scripts
# @Desc    : 京东APP->签到领金豆->摇京豆
import aiohttp
import asyncio
import re
import json

from urllib.parse import unquote
from utils.console import println
from utils.process import process_start


class LotteryBean:







    """
    抽京豆
    """
    headers = {
        'referer': 'https://turntable.m.jd.com',
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._pt_pin = unquote(pt_pin)

    async def lottery(self, session):
        """
        抽金豆
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=lotteryDraw&body=%7B%22actId%22%3A%22jgpqtzjhvaoym%22%2C' \
              '%22appSource%22%3A%22jdhome%22%2C%22lotteryCode%22%3A' \
              '%223zt5mf6evl5h4oe4mwfpueshk5nsyuqrssvzwf55qfcenlog7kavbf5cyrs6kbnphiawzpccizuck%22%7D&appid=ld&client' \
              '=android&clientVersion=&networkType=wifi&osVersion=&uuid=&jsonp=jsonp_1624843889411_61314'
        try:
            response = await session.get(url=url)
            text = await response.text()
            text = re.findall(r'\((.*?)\);', text)[0]
            data = json.loads(text)
            if data['code'] != '0':
                println('{}, 抽京豆失败, {}'.format(self._pt_pin, data))
            elif 'errorMessage' in data:
                println('{}, 抽京豆失败, {}'.format(self._pt_pin, data['errorMessage']))
            else:
                println('{}, 抽京豆成功, 中奖信息: {}'.format(self._pt_pin, data['data']['toastTxt']))

        except Exception as e:
            println('{}, 抽京豆错误!{}'.format(self._pt_pin, e.args))

    async def run(self):
        """
        程序入口
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            await self.lottery(session)


def start(pt_pin, pt_key):
    """
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = LotteryBean(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    process_start(start, '抽京豆')
