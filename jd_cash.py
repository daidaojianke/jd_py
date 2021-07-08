#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/8 5:43 下午
# @File    : jd_cash.py
# @Project : jd_scripts
# @Desc    : 签到领现金
import aiohttp
import asyncio

import json
from urllib.parse import quote, unquote
from utils.console import println


class JdCash:
    """
    签到领现金
    """
    headers = {
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'api.m.jd.com',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Referer': 'http://wq.jd.com/wxapp/pages/hd-interaction/index/index',
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._pt_pin = unquote(pt_pin)
        self._invite_code = None
        self._share_date = None

    async def request(self, session, function_id, body=None):
        """
        :param function_id:
        :param body:
        :return:
        """
        if body is None:
            body = {}
        url = 'https://api.m.jd.com/client.action?functionId={}&body={}' \
              '&appid=CashRewardMiniH5Env&appid=9.1.0'.format(function_id, quote(json.dumps(body)))
        try:
            response = await session.get(url=url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0:
                return {
                    'bizCode': 9999
                }
            else:
                if data['data']['bizCode'] != 0:
                    return data['data']
                else:
                    data = data['data']['result']
                    data['bizCode'] = 0
                    return data
        except Exception as e:
            println('{}, 获取服务器数据失败:{}!'.format(self._pt_pin, e.args))
            return {
                'bizCode': 9999
            }

    async def do_tasks(self, session):
        """
        做任务
        :param session:
        :return:
        """
        data = await self.request(session, 'cash_mob_home')
        if data['bizCode'] != 0:
            println('{}, 无法获取活动首页数据!'.format(self._pt_pin))
            return
        self._invite_code = data['inviteCode']  # 邀请码
        self._share_date = data['shareDate']
        task_list = list(data['taskInfos'])

        for task in task_list:
            for i in range(task['doTimes'], task['times']):
                println('{}, 正在进行任务:{}, 进度:{}/{}!'.format(self._pt_pin, task['name'], task['doTimes'], task['times']))

    async def run(self):
        """
        入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            await self.do_tasks(session)


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdCash(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())