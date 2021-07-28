#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/13 3:31 下午
# @File    : jd_smash_golden_egg.py
# @Project : jd_scripts
# @Desc    : 京东APP->每日特价->疯狂砸金蛋
import aiohttp
import asyncio
import json

from urllib.parse import quote, unquote
from utils.console import println
from config import USER_AGENT, JD_SMASH_GOLDEN_EGG_CODE


class JdSmashGoldenEgg:
    """
    京东APP->每日特价->疯狂砸金蛋
    :return:
    """

    def __init__(self, pt_pin, pt_key):
        """
        砸金蛋
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._headers = {
            'user-agent': USER_AGENT,
        }
        self._pt_pin = unquote(pt_pin)

    async def request(self, session, function_id, body=None):
        """
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        try:
            if body is None:
                body = {}
            url = 'https://api.m.jd.com/client.action?' \
                  'functionId={}&body={}&client=wh5&clientVersion=1.0.0'.format(function_id, quote(json.dumps(body)))
            response = await session.post(url=url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0:
                return data
            else:
                return data['data']
        except Exception as e:
            println('{}, 访问服务器失败:{}!'.format(self._pt_pin, e.args))
            return {
                'bizCode': 999,
                'bizMsg': '访问服务器失败'
            }

    async def get_home_data(self, session):
        """
        获取首页数据
        :param session:
        :return:
        """
        data = await self.request(session, 'interact_template_getHomeData', {"appId": "1EFRQwA", "taskToken": ""})
        return data

    async def help_friend(self, session, task):
        """
        助力好友
        :param session:
        :param task:
        :return:
        """
        my_code = task['assistTaskDetailVo']['taskToken']
        for code in JD_SMASH_GOLDEN_EGG_CODE:
            if code == my_code:
                continue
            body = {
                "appId": "1EFRQwA",
                "taskToken": code,
                "taskId": int(task['taskId']),
                "actionType": 0
            }
            res = await self.request(session, 'harmony_collectScore', body)
            if res['bizCode'] != 0:
                println('{}, 助力好友:{}失败!'.format(self._pt_pin, code))
                break
            else:
                println('{}, 成功助力好友:{}!'.format(self._pt_pin, code))
            await asyncio.sleep(1)

    async def sign(self, session, task):
        """
        签到
        :param session:
        :param task:
        :return:
        """
        task_name = task['taskName']

        res = await self.request(session, 'harmony_collectScore', {
            "appId": "1EFRQwA",
            "taskToken": task['simpleRecordInfoVo']['taskToken'],
            "taskId": task['taskId'],
            "actionType": 0
        })
        if res['bizCode'] == 0:
            println('{}, 成功完成任务: 《{}》'.format(self._pt_pin, task_name))
        else:
            println('{}, 完成任务: 《{}》失败, 原因: {}'.format(self._pt_pin, task_name, res['bizMsg']))

    async def do_task(self, session, task):
        """
        做任务
        :param session:
        :param task:
        :return:
        """
        if 'productInfoVos' in task:
            item_list = task['productInfoVos']
            task_name = '浏览商品'
        elif 'shoppingActivityVos' in task:
            item_list = task['shoppingActivityVos']
            task_name = '浏览会场'
        elif 'followShopVo' in task:
            item_list = task['followShopVo']
            task_name = '关注店铺'
        elif 'brandMemberVos' in task:
            item_list = task['brandMemberVos']
            task_name = '加入会员'
        else:
            item_list = []
            task_name = '未知'

        for item in item_list:
            res = await self.request(session, 'harmony_collectScore', {
                "appId": "1EFRQwA",
                "taskToken": item['taskToken'],
                "taskId": task['taskId'],
                "actionType": 0
            })
            if res['bizCode'] == 0:
                println('{}, 成功完成任务: 《{}》'.format(self._pt_pin, task_name))
            else:
                println('{}, 完成任务: 《{}》失败, 原因{}:'.format(self._pt_pin, task_name, res['bizMsg']))

    async def do_tasks(self, session, data):
        """
        做任务
        :param session:
        :param data: 首页数据
        :return:
        """
        println('{}, 开始做任务...'.format(self._pt_pin))
        for task in data['result']['taskVos']:

            task_type = task['taskType']
            task_name = task['taskName']
            task_status = task['status']
            if task_status == 2:
                println('{}, 任务:《{}》今日已完成!'.format(self._pt_pin, task_name))
                continue
            if task_type == 13:
                await self.sign(session, task)
            elif task_type == 14:
                await self.help_friend(session, task)
            elif task_type == 21:
                println('{}, 跳过任务: 《{}》!'.format(self._pt_pin, task_name))
                continue
            else:
                await self.do_task(session, task)

    async def get_share_code(self):
        """
        获取助力码
        :return:
        """
        async with aiohttp.ClientSession(headers=self._headers, cookies=self._cookies) as session:
            data = await self.get_home_data(session)
            if not data or data['bizCode'] != 0:
                println('{}, 无法获取助力码!'.format(self._pt_pin))
                return None
            for task in data['result']['taskVos']:
                if task['taskType'] == 14:
                    code = task['assistTaskDetailVo']['taskToken']
                    println('{}, 助力码:{}'.format(self._pt_pin, code))
                    return code
            return None

    async def do_lottery(self, session):
        """
        抽奖
        :param session:
        :return:
        """
        while True:
            res = await self.request(session, 'interact_template_getLotteryResult', {"appId": "1EFRQwA"})
            if res['bizCode'] == 0:
                println('{}, 抽奖成功, 结果:{}!'.format(self._pt_pin, res['result']))
            else:
                println('{}, 抽奖失败, {}'.format(self._pt_pin, res['bizMsg']))
                break
            await asyncio.sleep(0.5)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self._headers, cookies=self._cookies) as session:
            data = await self.get_home_data(session)
            if not data or data['bizCode'] != 0:
                println('{}, 无法获取首页数据, 退出程序...'.format(self._pt_pin))
                return
            await self.do_tasks(session, data)
            await self.do_lottery(session)


def start(pt_pin, pt_key):
    """
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdSmashGoldenEgg(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    # from config import JD_COOKIES
    # start(*JD_COOKIES[0].values())
    from utils.process import process_start
    process_start(start, '疯狂砸金蛋')