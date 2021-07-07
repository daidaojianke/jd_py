#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/21 9:58 上午
# @File    : jd_ranking_list.py
# @Project : jd_scripts
# @Desc    : 京东排行榜
import asyncio
import json

import aiohttp
from urllib.parse import unquote

from utils.notify import notify
from utils.console import println
from utils.logger import logger
from utils.process import process_start


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
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._account = '账号:{}'.format(unquote(pt_pin))
        self._bean_count = 0  # 获得金豆总数
        self._msg_list = []

    async def query_task(self, session):
        """
        查询任务
        :return:
        """
        task_list = []

        url = 'https://api.m.jd.com/client.action?functionId=queryTrumpTask&body=%7B%22sign%22%3A2%7D&appid' \
              '=content_ecology&clientVersion=9.2.0&client=wh5'
        try:
            response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            await asyncio.sleep(1)
            if data['code'] != '0':
                println('{}, 获取任务列表失败...'.format(self._account))
            else:
                task_list = data['result']['taskList']
                task_list.append(data['result']['signTask'])
                println('{}, 查询任务成功！'.format(self._account))
        except Exception as e:
            logger.error('{}, 查询任务失败:{}'.format(self._account, e.args))

        return task_list

    async def do_task(self, session, task):
        """
        做任务
        :param session:
        :param task:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=doTrumpTask&body' \
              '=%7B%22taskId%22%3A{}%2C%22itemId%22%3A%22{}%22%2C%22sign%22%3A2%7D&appid' \
              '=content_ecology&clientVersion=9.2.0' \
              '&client=wh5'.format(task['taskId'], task['taskItemInfo']['itemId'])
        try:
            response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != '0':
                logger.info('{}, 做任务失败:{}'.format(self._account, data))
            else:
                self._bean_count += int(data['result']['lotteryScore'])
                self._msg_list.append('任务:{}, {}'.format(task['taskName'], data['result']['lotteryMsg']))
                println('{}, 完成任务:{}, {}'.format(self._account, task['taskName'],
                                                 data['result']['lotteryMsg'].replace('\n', '')))

        except Exception as e:
            logger.error('{}, 做任务失败: {}'.format(self._account, e.args))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            task_list = await self.query_task(session)
            for task in task_list:
                await self.do_task(session, task)
                await asyncio.sleep(1)

        message = '#########今日王牌#########\n\n{}\n'.format(self._account)
        for msg in self._msg_list:
            message += msg + '\n'
        message += '总共获得:{}京豆!\n\n#########今日王牌#########\n'.format(self._bean_count)
        notify(message)


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdRankingList(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    process_start(start, '京东排行榜')
