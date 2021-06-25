#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/24 19:43
# @File    : jd_earn_bean.py
# @Project : jd_scripts
# @Desc    : JD APP首页->领金豆->升级赚京豆, 有签名, 需要反编译, 先放着
import asyncio
import time
import urllib.parse

import aiohttp
import json

from urllib.parse import unquote, quote

from config import USER_AGENT

from utils.notify import push_message_to_tg
from utils.logger import logger
from utils.console import println
from utils.process import process_start


class JdEarnBean:
    """
    JD APP 赚京豆
    """
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'jdmall;android;version/10.0.4;build/88641;os/11;'
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

    async def get_task_list(self, session):
        url = 'https://api.m.jd.com/client.action?functionId=beanTaskList&clientVersion=10.0.4&client=android&uuid' \
              '=a27b83d3d1dba1cc&st=1624534870477&sign=64667459b21e1ceff17291d32d14b7de&sv=121'
        body = 'body=%7B%7D&'
        try:
            response = await session.post(url, data=body)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != '0':
                println('获取任务列表失败!')
            else:
                return data['data']['taskInfos']
        except Exception as e:
            println('获取任务列表失败, 异常:{}'.format(e.args))

    async def do_task(self, session, task_token):
        """
        执行单个任务
        :param task:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=beanDoTask&clientVersion=10.0.5&client=android&uuid' \
              '=a27b83d3d1dba1cc&st=1624539309528&sign=629ee666baa3097a445a1b0f99320d90&sv=110'
        body = 'body={}'.format(quote(json.dumps({
                'actionType': 0,
                'taskToken': task_token,
            })))
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            println(text)
        except Exception as e:
            println(e.args)

    async def do_task_list(self, session, task_list):
        """
        处理任务列表
        :param task_list:
        :return:
        """
        for task in task_list:
            println('{}, 开始执行任务: {}, 共{}个子任务!'.format(self._pt_pin, task['taskName'], len(task['subTaskVOS'])))

            sub_task_list = task['subTaskVOS']

            for sub_task in sub_task_list:
                println('{}, 正在完成: {}->{}'.format(self._pt_pin, task['taskName'], sub_task['title']))
                await self.do_task(session, sub_task['taskToken'])
            println('{}, 任务:{}, 已完成!'.format(self._pt_pin, task['taskName']))
            break

    async def run(self):
        """
        程序入口
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            task_list = await self.get_task_list(session)
            await self.do_task_list(session, task_list)


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdEarnBean(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    pt_pin, pt_key = JD_COOKIES[0].values()
    start(pt_pin, pt_key)
    # process_start(start, '赚京豆')
