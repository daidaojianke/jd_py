#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/7 21:48
# @File    : jd_wishing_pool.py
# @Project : jd_scripts
# @Cron    : 45 */12 * * *
# @Desc    : 众筹许愿池,
import json
import re
import aiohttp
import asyncio

from urllib.parse import quote, unquote
from config import USER_AGENT, JD_WISHING_POOL_CODE
from utils.console import println


class JdWishingPool:
    """
    众筹许愿池
    """

    # 请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://h5.m.jd.com/babelDiy/Zeus/UQwNm9fNDey3xNEUTSgpYikqnXR/index.html',
        'User-Agent': USER_AGENT
    }

    def __init__(self, pt_pin, pt_key):
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._pt_pin = unquote(pt_pin)

    async def request(self, session, function_id, body=None):
        """
        请求数据
        """
        try:
            if body is None:
                body = {}

            url = 'https://api.m.jd.com/client.action?functionId={}&body={}&client=wh5&clientVersion=1.0.0' \
                .format(function_id, quote(json.dumps(body)))
            response = await session.post(url=url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0:
                return data
            else:
                return data['data']
        except Exception as e:
            println('{}, 访问服务器出错:{}!'.format(self._pt_pin, e.args))

    async def get_task_list(self, session):
        """
        获取任务列表
        """
        data = await self.request(session, 'healthyDay_getHomeData', {"appId": "1EFVQwQ",
                                                                      "taskToken": "", "channelId": 1})
        if 'bizCode' not in data or data['bizCode'] != 0:
            println('{}, 无法获取首页数据!'.format(self._pt_pin))
            return None
        return data['result']['taskVos']

    async def do_tasks(self, session, task_list):
        """
        做任务
        """
        for task in task_list:
            task_token = re.search(r"'taskToken': '(.*?)'", str(task)).group(1)
            if task['status'] == 2:
                println('{}, 任务：《{}》今日已完成!'.format(self._pt_pin, task['taskName']))
                continue
            if task['taskType'] == 14:
                for code in JD_WISHING_POOL_CODE:
                    if code == task_token:
                        continue
                    res = await self.request(session, 'harmony_collectScore', {
                        "appId": "1EFVQwQ",
                        "taskToken": code,
                        "taskId": task['taskId'],
                        "actionType": 1
                    })
                    if res['bizCode'] != 0:
                        println('{}, 助力好友失败, {}'.format(self._pt_pin, res['bizMsg']))
                        if res['bizCode'] == 108:  # 助力已上限
                            break
                    else:
                        println('{}, 成功助力一名好友!'.format(self._pt_pin))

                    await asyncio.sleep(1)

                continue

            wait_duration = 5 if task['waitDuration'] > 5 else 1
            for i in range(task['times'], task['maxTimes']):
                await asyncio.sleep(1)
                res = await self.request(session, 'harmony_collectScore', {
                    "appId": "1EFVQwQ",
                    "taskToken": task_token,
                    "taskId": task['taskId'],
                    "actionType": 1
                })
                if res['bizCode'] != 0 and res['bizCode'] != 1:
                    println('{}, 领取任务《{}》失败, {}!'.format(self._pt_pin, task['taskName'], res['bizMsg']))
                else:
                    println('{}, 领取任务《{}》成功!'.format(self._pt_pin, task['taskName']))

                println('{}, 任务:《{}》需要等待{}s!'.format(self._pt_pin, task['taskName'], wait_duration))
                await asyncio.sleep(wait_duration)

                res = await self.request(session, 'harmony_collectScore', {
                    "appId": "1EFVQwQ",
                    "taskToken": task_token,
                    "taskId": task['taskId'],
                    "actionType": 0
                })
                if res['bizCode'] != 0:
                    println('{}, 完成任务:《{}》失败!'.format(self._pt_pin, task['taskName']))
                else:
                    println('{}, 完成任务:《{}》, 获得金币:{}!'.format(self._pt_pin, task['taskName'], res['result']['score']))

    async def lottery(self, session):
        """
        抽奖
        """
        while True:
            res = await self.request(session, 'interact_template_getLotteryResult', {"appId": "1EFVQwQ"})

            if res['bizCode'] != 0:
                println('{}, 抽奖失败, {}!'.format(self._pt_pin, res['bizMsg']))
                break
            else:
                award_info = res['result']['userAwardsCacheDto']
                if 'jBeanAwardVo' in award_info:
                    message = award_info['jBeanAwardVo']['quantity'] + award_info['jBeanAwardVo']['ext']
                else:
                    message = award_info

                println('{}, 抽奖成功, 获得:{}!'.format(self._pt_pin, message))
            await asyncio.sleep(1)

    async def get_share_code(self):
        """
        获取助力码
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            data = await self.get_task_list(session)
            if not data:
                return None
            for item in data:
                if item['taskType'] == 14:
                    code = re.search(r"'taskToken': '(.*?)'", str(item)).group(1)
                    println('{}, 助力码:{}!'.format(self._pt_pin, code))
                    return code

    async def run(self):
        """
        程序入口
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            task_list = await self.get_task_list(session)
            if not task_list:
                println('{}， 无法获取数据, 退出程序!'.format(self._pt_pin))
                return
            await self.do_tasks(session, task_list)
            await self.lottery(session)


def start(pt_pin, pt_key, name='众筹许愿池'):
    """
    程序入口
    """
    try:
        app = JdWishingPool(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    # from config import JD_COOKIES
    # start(*JD_COOKIES[0].values())
    from utils.process import process_start
    process_start(start, '众筹许愿池')
