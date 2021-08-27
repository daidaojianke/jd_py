#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/27 10:56 上午
# @File    : jd_wonderful_lottery.py
# @Project : jd_scripts
# @Cron    : 44 4,5 * * *
# @Desc    : 京东APP->签到领豆->边玩边赚->每日抽奖
import asyncio
import json

import aiohttp

from utils.jd_init import jd_init
from utils.console import println
from config import USER_AGENT
from db.model import Code
from utils.process import process_start, get_code_list

CODE_KEY = 'jd_wonderful_lottery'


@jd_init
class JdWonderfulLottery:
    """
    京东精彩
    """
    headers = {
        'origin': 'https://jingcai-h5.jd.com',
        'user-agent': 'jdapp;' + USER_AGENT,
        'lop-dn': 'jingcai.jd.com',
        'accept': 'application/json, text/plain, */*',
        'appparams': '{"appid":158,"ticket_type":"m"}',
        'content-type': 'application/json',
        'referer': 'https://jingcai-h5.jd.com/index.html'
    }

    activityCode = "1419494729103441920"

    async def request(self, session, path, body=None, method='POST'):
        """
        请求服务器数据
        :return:
        """
        try:
            if not body:
                body = {}
            url = 'https://lop-proxy.jd.com/' + path
            if method == 'POST':
                response = await session.post(url, json=body)
            else:
                response = await session.get(url, json=body)

            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            println('{}, 请求服务器数据失败, {}'.format(self.account, e.args))
            return {
                'success': False
            }

    async def do_tasks(self, session):
        """
        做任务
        :return:
        """
        res = await self.request(session, '/luckdraw/queryMissionList', [{
            "userNo": "$cooMrdGatewayUid$",
            "activityCode": self.activityCode
        }])
        if not res.get('success'):
            println('{}, 获取任务列表失败!'.format(self.account))
            return
        task_list = res['content']['missionList']

        for task in task_list:
            if task['status'] == 10:
                println('{}, 今日完成任务:{}!'.format(self.account, task['title']))
                continue

            if task['status'] == 11:
                for no in task['getRewardNos']:
                    body = [{
                        "activityCode": self.activityCode,
                        "userNo": "$cooMrdGatewayUid$",
                        "getCode": no
                    }]
                    res = await self.request(session, '/luckDraw/getDrawChance', body)
                    if res.get('success'):
                        println('{}, 成功领取一次抽奖机会!'.format(self.account))
                        break
                continue

            if '邀请' in task['title']:  # 邀请好友
                code = task['missionNo']
                println('{}, 助力码:{}'.format(self.account, code))
                Code.insert_code(code_val=code, code_key=CODE_KEY, sort=self.sort, account=self.account)
                continue

            for i in range(task['completeNum'], task['totalNum']):
                body = [{
                    "activityCode": self.activityCode,
                    "userNo": "$cooMrdGatewayUid$",
                    "missionNo": task['missionNo'],
                    "params": task['params']
                }]
                res = await self.request(session, '/luckDraw/completeMission', body)
                if res.get('success'):
                    println('{}, 完成任务:{}-{}'.format(self.account, task['title'], i + 1))
                await asyncio.sleep(1)

    async def run_help(self):
        """
        助力好友
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            item_list = Code.get_code_list(code_key=CODE_KEY)
            item_list.extend(get_code_list(code_key=CODE_KEY))
            for item in item_list:
                account, code = item.get('account'), item.get('code')
                if account == self.account:
                    continue
                res = await self.request(session, '/luckdraw/helpFriend', [{
                    "userNo": "$cooMrdGatewayUid$",
                    "missionNo": code
                }])
                if res.get('success'):
                    println('{}, 成功助力好友:{}'.format(self.account, account))
                else:
                    println('{}, 无法助力好友:{}'.format(self.account, account))

    async def lottery(self, session):
        """
        抽奖
        :return:
        """
        while True:
            res = await self.request(session, '/luckdraw/draw', [{
                "userNo": "$cooMrdGatewayUid$",
                "activityCode": self.activityCode
            }])
            if res.get('success'):
                println('{}, 抽奖成功'.format(self.account))
            else:
                break
            await asyncio.sleep(1)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.do_tasks(session)  # 做任务
            await self.lottery(session)  # 抽奖


if __name__ == '__main__':
    process_start(JdWonderfulLottery, '精彩-每日抽奖', code_key=CODE_KEY)
