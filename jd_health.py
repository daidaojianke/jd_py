#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/4 4:12 下午
# @File    : jd_health.py
# @Project : jd_scripts
# @Desc    : 东东健康社区
import asyncio
import aiohttp
import json
from urllib.parse import urlencode
from utils.wraps import jd_init
from utils.console import println
from config import USER_AGENT

ERRCODE_DEFAULT = 9999


@jd_init
class JdHealth:
    """
    东东健康社区
    """
    headers = {
        'user-agent': 'jdapp;' + USER_AGENT,
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://h5.m.jd.com',
        'referer': 'https://h5.m.jd.com/',
    }

    async def request(self, session, function_id, body=None, method='POST'):
        """
        请求数据
        :param session:
        :param function_id:
        :param body:
        :param method:
        :return:
        """
        try:
            if not body:
                body = {}
            params = {
                'functionId': function_id,
                'client': 'wh5',
                'body': json.dumps(body),
                'clientVersion': '1.0.0',
                'uuid': '0'
            }
            url = 'https://api.m.jd.com/?' + urlencode(params)
            if method == 'POST':
                response = await session.post(url=url)
            else:
                response = await session.get(url=url)

            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0:
                return {
                    'bizCode': ERRCODE_DEFAULT,
                    'bizMsg': data['msg']
                }
            else:
                return data['data']

        except Exception as e:
            println('{}, 获取服务器数据失败:{}!'.format(self.account, e.args))
            return {
                'bizCode': ERRCODE_DEFAULT,
                'bizMsg': '获取服务器数据失败!'
            }

    async def get_task_list(self, session):
        """
        获取任务列表
        :return:
        """
        function_id = 'jdhealth_getTaskDetail'
        body = {"buildingId": "", "taskId": "", "channelId": 1}
        res = await self.request(session, function_id, body)
        return res.get('result', dict()).get('taskVos', list())

    async def clockIn(self, session, task):
        """
        早起打卡
        :param session:
        :param task:
        :return:
        """
        function_id = 'jdhealth_collectScore'
        task_token = task['threeMealInfoVos'][0]['taskToken']
        body = {"taskToken": task_token, "taskId": task['taskId'], "actionType": 0}
        res = await self.request(session, function_id, body)
        if res.get('bizCode', ERRCODE_DEFAULT) == 0:
            println('{}, 打卡成功!'.format(self.account))
        else:
            println('{}, 打卡失败, {}'.format(self.account, res.get('bizMsg', '原因未知')))

    async def receive_task(self, session, task_id, task_token):
        """
        领取任务
        :param session:
        :param task_id:
        :param task_token:
        :return:
        """
        function_id = 'jdhealth_collectScore'

        body = {
            'taskId': task_id,
            'taskToken': task_token,
            "actionType": 1,
        }

        return await self.request(session, function_id, body)

    async def receive_task_award(self, session, task_id, task_token):
        """
        领取任务奖励
        :param session:
        :param task_id:
        :param task_token:
        :return:
        """
        function_id = 'jdhealth_collectScore'

        body = {
            'taskId': task_id,
            'taskToken': task_token,
            "actionType": 0,
        }

        return await self.request(session, function_id, body)

    async def browser_task(self, session, task, item_list_key='shoppingActivityVos', task_name=None):
        """
        浏览商品
        :param task_name:
        :param item_list_key:
        :param session:
        :param task:
        :return:
        """
        if not task_name:
            task_name = task.get('taskName')

        task_id = task['taskId']

        item_list = task[item_list_key]

        times, max_times = task['times'], task['maxTimes']

        if times == 0:
            times += 1

        for item in item_list:
            if times > max_times:
                break
            res = await self.receive_task(session, task_id, item['taskToken'])
            println('{}, 领取任务《{}》{}/{}, {}!'.format(self.account, task_name, times, max_times,
                                                    res.get('bizMsg')))
            if res.get('bizCode', ERRCODE_DEFAULT) == 105:
                break
            times += 1
            await asyncio.sleep(1)

        timeout = task.get('waitDuration', 1)
        if timeout < 1:
            timeout = 1
        println('{}, {}秒后去领取任务《{}》奖励...'.format(self.account, timeout, task_name))
        await asyncio.sleep(timeout)

        times, max_times = task['times'], task['maxTimes']

        if times == 0:
            times += 1

        for item in item_list:
            if times > max_times:
                break
            res = await self.receive_task_award(session, task_id, item['taskToken'])
            println('{}, 领取任务《{}》{}/{}奖励, {}!'.format(self.account, task_name,
                                                      times, max_times, res.get('bizMsg')))
            times += 1
            if res.get('bizCode', ERRCODE_DEFAULT) == 105:
                break
            await asyncio.sleep(1)

    async def do_task_list(self, session, task_list):
        """
        做任务
        :param task_list:
        :param session:
        :return:
        """
        for task in task_list:

            task_type, task_name = task.get('taskType'), task.get('taskName')

            if task['status'] == 2:
                println('{}, 任务《{}》已做完!'.format(self.account, task_name))
                continue

            if task_type == 19:  # 下单任务
                println('{}, 跳过任务:《{}》!'.format(self.account, task_name))
                continue
            elif task_type == 10:  # 早起打卡
                await self.clockIn(session, task)
            elif task_type == 9:  # 逛商品
                await self.browser_task(session, task, 'shoppingActivityVos')
            elif task_type == 1:  # 关注店铺
                await self.browser_task(session, task, 'followShopVo')
            elif task_type in [3, 8, 25]:  # 浏览产品
                if 'shoppingActivityVos' in task:
                    await self.browser_task(session, task, 'shoppingActivityVos')
                else:
                    await self.browser_task(session, task, 'productInfoVos')
            else:
                println(task_type, task_name)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            task_list = await self.get_task_list(session)

            await self.do_task_list(session, task_list)


if __name__ == '__main__':
    from config import JD_COOKIES

    app = JdHealth(**JD_COOKIES[8])
    asyncio.run(app.run())
