#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:27 下午
# @File    : jd_farm.py
# @Project : jd_scripts
# @Desc    : 京东APP-东东农场
import asyncio
import aiohttp
import json

from urllib.parse import unquote, urlencode
from utils.console import println
from config import USER_AGENT


class JdFarm:
    """
    京东农场
    """
    headers = {
        'user-agent': USER_AGENT,
        # 'content-type': 'application/json',
        'x-requested-with': 'com.jingdong.app.mall',
        'sec-fetch-mode': 'cors',
        'origin': 'https://carry.m.jd.com',
        'sec-fetch-site': 'same-site',
        'referer': 'https://carry.m.jd.com/babelDiy/Zeus/3KSjXqQabiTuD1cJ28QskrpWoBKT/index.html'
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._pt_pin = unquote(pt_pin)
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._farm_info = None

    async def request(self, session, function_id, body=None):
        """
        :param session:
        :param body:
        :param function_id:
        :return:
        """
        try:
            if not body:
                body = dict()
            body['version'] = 13
            body['channel'] = 1

            url = 'https://api.m.jd.com/client.action?functionId={}&body={}&appid=wh5'.format(function_id,
                                                                                              json.dumps(body))
            response = await session.get(url=url)
            data = await response.json()
            return data
        except Exception as e:
            println('{}, 获取服务器数据错误:{}'.format(self._pt_pin, e.args))

    async def init_for_farm(self, session):
        """
        初始化农场数据
        :param session:
        :return:
        """
        data = await self.request(session, 'initForFarm')
        if data['code'] != '0' or 'farmUserPro' not in data:
            return None
        return data['farmUserPro']

    async def sign(self, session):
        """
        :param session:
        :return:
        """
        data = await self.request(session, 'signForFarm')
        if data['code'] == '0':
            println('{}, 签到成功, 已连续签到{}天!'.format(self._pt_pin, data['signDay']))
        elif data['code'] == '7':
            println('{}, 今日已签到过!'.format(self._pt_pin))
        else:
            println('{}, 签到失败, {}'.format(self._pt_pin, data['message']))

        if 'todayGotWaterGoalTask' in data and data['todayGotWaterGoalTask']['canPop']:
            await asyncio.sleep(1)
            data = await self.request(session, 'gotWaterGoalTaskForFarm', {'type': 3})
            if data['code'] == '0':
                println('{}, 被水滴砸中, 获得{}g水滴!'.format(self._pt_pin, data['addEnergy']))

    async def do_browser_tasks(self, session, tasks):
        """
        做浏览任务
        :param tasks:
        :param session:
        :return:
        """
        await asyncio.sleep(1)
        for task in tasks:
            task_name = task['mainTitle']
            println('{}, 正在进行浏览任务: 《{}》...'.format(self._pt_pin, task_name))
            task_res = await self.request(session, 'browseAdTaskForFarm', {'advertId': task['advertId'], 'type': 0})
            # 完成任务去领取奖励
            if task_res['code'] == '0' or task_res['code'] == '7':
                task_award = await self.request(session, 'browseAdTaskForFarm', {'advertId': str(task['advertId']), 'type': 1})
                if task_award['code'] == '0':
                    println('{}, 成功领取任务:《{}》的奖励, 获得{}g水滴！'.format(self._pt_pin, task_name, task_award['amount']))
                else:
                    println('{}, 领取任务:《{}》的奖励失败, {}'.format(self._pt_pin, task_name, task_award))
            else:
                println('{}, 浏览任务:《{}》, 结果:{}'.format(self._pt_pin, task_name, task_res))

    async def get_award_of_invite_friend(self, session):
        """
        获取邀请好友奖励
        :param session:
        :return:
        """
        data = await self.request(session, 'friendListInitForFarm')
        println(data)

    async def timed_collar_drop(self, session):
        """
        定时领水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'gotThreeMealForFarm')
        if data['code'] == '0':
            println('{}, 【定时领水滴】获得 {}g!'.format(self._pt_pin, data['amount']))
        else:
            println('{}, 【定时领水滴】失败,{}!'.format(self._pt_pin, data))

    async def do_daily_task(self, session):
        """
        领水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'taskInitForFarm')
        if data['code'] != '0':
            println('{}, 获取领水滴任务列表失败!'.format(self._pt_pin))
            return
        today_signed = data['signInit']['todaySigned']

        if not today_signed:  # 签到任务
            await self.sign(session)
        else:
            println('{}, 今日已签到, 已连续签到{}天!'.format(self._pt_pin, data['signInit']['totalSigned']))

        if not data['gotBrowseTaskAdInit']['f']:  # 浏览任务
            tasks = data['gotBrowseTaskAdInit']['userBrowseTaskAds']
            await self.do_browser_tasks(session, tasks)
        else:
            println('{}, 今日浏览广告任务已完成!'.format(self._pt_pin))

        if not data['gotThreeMealInit']['f']:  # 定时领水
            await self.timed_collar_drop(session)

        if not data['waterFriendTaskInit']['f'] and \
                data['waterFriendTaskInit']['waterFriendCountKey'] < data['waterFriendTaskInit']['waterFriendMax']:
            pass

        # await self.get_award_of_invite_friend(session)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            self._farm_info = await self.init_for_farm(session=session)
            if not self._farm_info:
                println('{}, 无法获取农场数据, 退出程序!'.format(self._pt_pin))
                return
            await self.do_daily_task(session)   # 每日任务


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdFarm(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())
