#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/21 9:58 上午
# @File    : jd_ranking_list.py
# @Project : jd_scripts
# @Desc    : 京东排行榜
import asyncio
import json

import aiohttp

from utils.console import println
from config import JD_COOKIES
from utils.logger import logger


class JdRankingList:
    """
    京东排行榜
    """

    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://h5.m.jd.com/babelDiy/Zeus/3wtN2MjeQgjmxYTLB3YFcHjKiUJj/index.html',
        'Host': 'api.m.jd.com',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-cn'
    }

    def __init__(self, pt_pin='', pt_key=''):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._pt_pin = pt_pin
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }

    async def query_task(self, session):
        """
        查询任务
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=queryTrumpTask&body=%7B%22sign%22%3A2%7D&appid' \
              '=content_ecology&clientVersion=9.2.0&client=wh5'
        response = await session.post(url)
        text = await response.text()
        data = json.loads(text)
        # data['result']['signTask']['taskItemInfo']
        return data['result']['taskList']

    async def do_task(self, session, task):
        """
        :param session:
        :param task:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=doTrumpTask&body' \
              '=%7B%22taskId%22%3A{}%2C%22itemId%22%3A%22{}%22%2C%22sign%22%3A2%7D&appid' \
              '=content_ecology&clientVersion=9.2.0'\
              '&client=wh5'.format(task['taskId'], task['taskItemInfo']['itemId'])
        response = await session.post(url)
        text = await response.text()
        logger.info(text)
        data = json.loads(text)
        lottery_msg = data['result']['lotteryMsg']
        println(data)

    async def sign(self, session):
        """
        :param session:
        :return:
        """
        pass

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            task_list = await self.query_task(session)
            for task in task_list:
                await self.do_task(session, task)
                break


if __name__ == '__main__':
    from config import JD_COOKIES

    for jd_cookie in JD_COOKIES:
        app = JdRankingList(jd_cookie['pt_pin'], jd_cookie['pt_key'])
        asyncio.run(app.run())
        break
