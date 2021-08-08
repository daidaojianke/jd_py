#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/13 3:31 下午
# @File    : jd_smash_golden_egg.py
# @Project : jd_scripts
# @Cron    : #45 5,19 * * *
# @Desc    : 京东APP->每日特价->疯狂砸金蛋
import aiohttp
import asyncio
import json

from urllib.parse import quote
from utils.console import println
from utils.jd_init import jd_init
from config import USER_AGENT
from db.model import Code, CODE_SMASH_GOLDEN_EGG


@jd_init
class JdSmashGoldenEgg:
    """
    京东APP->每日特价->疯狂砸金蛋
    :return:
    """
    headers = {
        'user-agent': USER_AGENT,
    }

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
            println('{}, 访问服务器失败:{}!'.format(self.account, e.args))
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
            println('{}, 成功完成任务: 《{}》'.format(self.account, task_name))
        else:
            println('{}, 完成任务: 《{}》失败, 原因: {}'.format(self.account, task_name, res['bizMsg']))

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
                println('{}, 成功完成任务: 《{}》'.format(self.account, task_name))
            else:
                println('{}, 完成任务: 《{}》失败, 原因{}:'.format(self.account, task_name, res['bizMsg']))

    async def do_tasks(self, session, data):
        """
        做任务
        :param session:
        :param data: 首页数据
        :return:
        """
        println('{}, 开始做任务...'.format(self.account))
        for task in data['result']['taskVos']:
            task_type = task['taskType']
            task_name = task['taskName']
            task_status = task['status']
            if task_status == 2:
                println('{}, 任务:《{}》今日已完成!'.format(self.account, task_name))
                continue
            if task_type == 13:
                await self.sign(session, task)
            elif task_type == 14:
                code = task['assistTaskDetailVo']['taskToken']
                println('{}, 助力码:{}'.format(self.account, code))
                from db.model import Code
                Code.insert_code(code_key=CODE_SMASH_GOLDEN_EGG, account=self.account, code_val=code)
            elif task_type == 21:
                println('{}, 跳过任务: 《{}》!'.format(self.account, task_name))
                continue
            else:
                await self.do_task(session, task)

    async def do_lottery(self, session):
        """
        抽奖
        :param session:
        :return:
        """
        while True:
            res = await self.request(session, 'interact_template_getLotteryResult', {"appId": "1EFRQwA"})
            if res['bizCode'] == 0:
                println('{}, 抽奖成功, 结果:{}!'.format(self.account, res['result']))
            else:
                println('{}, 抽奖失败, {}'.format(self.account, res['bizMsg']))
                break
            await asyncio.sleep(0.5)

    async def run(self):
        """
        任务入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            data = await self.get_home_data(session)
            if not data or data['bizCode'] != 0:
                println('{}, 无法获取首页数据, 退出程序...'.format(self.account))
                return
            await self.do_tasks(session, data)
            await self.do_lottery(session)

    async def run_help(self):
        """
        助力入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            item_list = Code.get_code_list(CODE_SMASH_GOLDEN_EGG)
            for item in item_list:
                friend_account, friend_code = item.get('account'), item.get('code')
                if self.account == friend_account:
                    continue
                body = {
                    "appId": "1EFRQwA",
                    "taskToken": friend_account,
                    "taskId": 6,
                    "actionType": 0
                }
                res = await self.request(session, 'harmony_collectScore', body)
                if res['bizCode'] != 0:
                    println('{}, 助力好友:{}失败, {}'.format(self.account, friend_account, res.get('bizMsg')))
                    if res['bizCode'] == 105:
                        break
                else:
                    println('{}, 成功助力好友:{}!'.format(self.account, friend_account))
                await asyncio.sleep(1)


if __name__ == '__main__':
    from utils.process import process_start
    process_start(JdSmashGoldenEgg, '疯狂砸金蛋')
