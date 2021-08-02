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
from utils.wraps import jd_init
from config import USER_AGENT, JD_WISHING_POOL_CODE
from utils.console import println


@jd_init
class JdWishingPool:
    """
    众筹许愿池
    """

    # 请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://h5.m.jd.com/babelDiy/Zeus/4FdmTJQNah9oDJyQN8NggvRi1nEY/index.html',
        'User-Agent': USER_AGENT
    }

    async def request(self, session, function_id, body=None):
        """
        请求数据
        """
        try:
            await asyncio.sleep(1)

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
            println('{}, 访问服务器出错:{}!'.format(self.account, e.args))

    async def get_task_list(self, session):
        """
        获取任务列表
        """
        data = await self.request(session, 'healthyDay_getHomeData', {"appId": "1E1NXxq0",
                                                                      "taskToken": "", "channelId": 1})
        if 'bizCode' not in data or data['bizCode'] != 0:
            println('{}, 无法获取首页数据!'.format(self.account))
            return None
        return data['result']['taskVos']

    async def help_friend(self, session, task_token, task_id):
        """
        :return:
        """
        for code in JD_WISHING_POOL_CODE:
            if code == task_token:
                continue
            res = await self.request(session, 'harmony_collectScore', {
                "appId": "1E1NXxq0",
                "taskToken": code,
                "taskId": task_id,
                "actionType": 1
            })
            if res['bizCode'] != 0:
                println('{}, 助力好友:{}失败, {}'.format(self.account, code, res['bizMsg']))
                if res['bizCode'] == 108:  # 助力已上限
                    break
            else:
                println('{}, 成功助力好友:{}!'.format(self.account, code))
            await asyncio.sleep(1)

    async def finish_task(self, session, task_token, task_id, task_name):
        """
        完成任务
        :param task_name:
        :param task_id:
        :param task_token:
        :param session:
        :return:
        """
        res = await self.request(session, 'harmony_collectScore', {
            "appId": "1E1NXxq0",
            "taskToken": task_token,
            "taskId": task_id,
            "actionType": 1
        })
        if res['bizCode'] != 0 and res['bizCode'] != 1:
            println('{}, 完成任务《{}》失败, {}!'.format(self.account, task_name, res['bizMsg']))
        else:
            println('{}, 完成任务《{}》成功!'.format(self.account, task_name))

    async def do_browse_task(self, session, task):
        """
        做浏览任务
        :param session:
        :param task:
        :return:
        """
        if 'productInfoVos' in task:
            item_list = task['productInfoVos']
        elif 'followShopVo' in task:
            item_list = task['followShopVo']
        else:
            item_list = []

        for item in item_list:
            println(item)
            task_token = item['taskToken']
            task_id = task['taskId']
            await self.finish_task(session, task_token, task_id, task['taskName'])

    async def do_tasks(self, session, task_list):
        """
        做任务
        """
        println('{}, 正在做任务!'.format(self.account))
        for task in task_list:
            task_token = re.search(r"'taskToken': '(.*?)'", str(task)).group(1)
            if task['status'] == 2:
                println('{}, 任务：《{}》今日已完成!'.format(self.account, task['taskName']))
                continue
            if task['taskType'] == 14:
                await self.help_friend(session, task_token, task['taskId'])
                continue

            if task['maxTimes'] > 1:
                await self.do_browse_task(session, task)
            else:
                await self.finish_task(session, task_token, task['taskId'], task['taskName'])

            res = await self.request(session, 'harmony_collectScore', {
                "appId": "1E1NXxq0",
                "taskToken": task_token,
                "taskId": task['taskId'],
                "actionType": 0
            })
            if res['bizCode'] != 0:
                println('{}, 领取任务:《{}》奖励失败!'.format(self.account, task['taskName']))
            else:
                println('{}, 领取任务:《{}》奖励成功, 获得金币:{}!'.format(self.account, task['taskName'], res['result']['score']))

    async def lottery(self, session):
        """
        抽奖
        """
        while True:
            res = await self.request(session, 'interact_template_getLotteryResult', {"appId":"1E1NXxq0"})

            if res['bizCode'] != 0:
                println('{}, 抽奖失败, {}!'.format(self.account, res['bizMsg']))
                break
            else:
                award_info = res['result']['userAwardsCacheDto']
                if 'jBeanAwardVo' in award_info:
                    message = award_info['jBeanAwardVo']['quantity'] + award_info['jBeanAwardVo']['ext']
                else:
                    message = award_info

                println('{}, 抽奖成功, 获得:{}!'.format(self.account, message))
            await asyncio.sleep(1)

    async def get_share_code(self):
        """
        获取助力码
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            data = await self.get_task_list(session)
            if not data:
                return None
            for item in data:
                if item['taskType'] == 14:
                    code = re.search(r"'taskToken': '(.*?)'", str(item)).group(1)
                    println('{}, 助力码:{}!'.format(self.account, code))
                    return code

    async def run(self):
        """
        程序入口
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            task_list = await self.get_task_list(session)
            if not task_list:
                println('{}， 无法获取数据, 退出程序!'.format(self.account))
                return
            await self.do_tasks(session, task_list)
            await self.lottery(session)


if __name__ == '__main__':
    # from config import JD_COOKIES
    # app = JdWishingPool(**JD_COOKIES[8])
    # asyncio.run(app.run())
    from utils.process import process_start
    process_start(JdWishingPool, '众筹许愿池')
