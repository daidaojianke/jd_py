#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/19 10:30
# @File    : jd_lucky_turntable.py
# @Project : jd_scripts
# @Desc    : 幸运大转盘, 活动地址: https://pro.m.jd.com/mall/active/3ryu78eKuLyY5YipWWVSeRQEpLQP/index.html
import asyncio
import json
import re
from urllib.parse import quote, unquote

import aiohttp

from utils.logger import logger
from utils.console import println
from utils.notify import notify
from config import USER_AGENT


class LuckyTurntable:
    headers = {
        'user-agent': USER_AGENT,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3',
        'x-requested-with': 'com.jingdong.app.mall',
        'Sec-Fetch-Mode': 'navigate',
        'referer': 'https://pro.m.jd.com/mall/active/3ryu78eKuLyY5YipWWVSeRQEpLQP/index.html?forceCurrentView=1'
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
        self._result = []
        self._message = None

    @property
    def message(self):
        return self._message

    async def get_task_list(self, session):
        """
        :param session:
        :return:
        """
        url = 'https://pro.m.jd.com/mall/active/3ryu78eKuLyY5YipWWVSeRQEpLQP/index.html?forceCurrentView=1'
        try:
            response = await session.get(url)
            text = await response.text()
            pattern = r'window.__react_data__ = (\{.*\})'

            temp = re.findall(pattern, text)

            task_list = []

            if len(temp) == 0:
                println('账号:{}, 匹配活动数据失败!'.format(self._pt_pin))
                return False

            data = json.loads(temp[0])
            if 'activityData' not in data or 'floorList' not in data['activityData']:
                return task_list

            for line in data['activityData']['floorList']:
                if 'template' in line and line['template'] == 'score_task':
                    task_list = line['taskItemList']

            return task_list

        except Exception as e:
            logger.info(e.args)

    async def do_task(self, session, en_award_k):
        """
        做任务
        :param session:
        :param en_award_k:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=babelDoScoreTask'
        params = {"enAwardK": en_award_k, "isQueryResult": 0, "siteClient": "apple", "mitemAddrId": "",
                  "geo": {"lng": "", "lat": ""}, "addressId": "", "posLng": "", "posLat": "", "homeLng": "",
                  "homeLat": "", "focus": "", "innerAnchor": "", "cv": "2.0"}
        session.headers.add('content-type', 'application/x-www-form-urlencoded')
        body = 'body={}&client=wh5&clientVersion=1.0.0'.format(quote(json.dumps(params)))

        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)

            if data['code'] == '0':
                self._result.append('{}, 当前积分:{}, 任务进度: {}'.format(data['promptMsg'],
                                                                   data['userScore'], data['taskProgress']))
                println('账号:{}, {}, 当前积分:{}, 任务进度: {}'.format(self._pt_pin, data['promptMsg'],
                                                              data['userScore'], data['taskProgress']))
                return data['userScore']
            else:
                println('账号:{}, 做任务失败, {}'.format(self._pt_pin, data))
        except Exception as e:
            logger.error('账号:{}, 做任务异常:{}'.format(self._pt_pin, e.args))

    async def lottery(self, session):
        """
        抽奖  a84f9428da0bb36a6a11884c54300582
        :param session:
        :return:
        """
        session.headers.add('origin', 'https://h5.m.jd.com')
        session.headers.add('referer', 'https://h5.m.jd.com/')
        session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
        home_url = 'https://pro.m.jd.com/mall/active/3ryu78eKuLyY5YipWWVSeRQEpLQP/index.html?forceCurrentView=1'
        lottery_url = 'https://api.m.jd.com/client.action?functionId=babelGetLottery'
        try:
            response = await session.get(home_url)
            text = await response.text()
            temp = re.findall(r'window.__react_data__ = (\{.*\})', text)
            if len(temp) == 0:
                println('账号:{}, 匹配活动数据失败!'.format(self._pt_pin))
                return False
            data = json.loads(temp[0])
            if 'activityData' not in data or 'floorList' not in data['activityData']:
                println('账号:{}, 匹配活动数据失败!'.format(self._pt_pin))
                return False

            user_score = 0
            en_award_k = None

            for line in data['activityData']['floorList']:
                if 'template' in line and line['template'] == 'choujiang_wheel':
                    user_score = line['lotteryGuaGuaLe']['userScore']
                    en_award_k = line['lotteryGuaGuaLe']['enAwardK']

            if user_score < 80:
                println('账号: {}, 积分:{}, 不够抽奖...'.format(self._pt_pin, user_score))
                self._result.append('积分:{}, 不够抽奖...'.format(user_score))
                return False

            if not en_award_k:
                println('账号: {}, 查找抽奖数据失败, 无法抽奖'.format(self._pt_pin))
                return False

            params = {
                'enAwardK': en_award_k,
                'authType': '2'
            }
            body = 'body={}&client=wh5&clientVersion=1.0.0'.format(quote(json.dumps(params)))
            response = await session.post(url=lottery_url, data=body)
            text = await response.text()
            data = json.loads(text)

            if data['code'] != '0':
                self._result.append('账号:{} 抽奖失败:{}'.format(self._pt_pin, data))
                println('抽奖失败:{}'.format(self._pt_pin, data))
                return False
            else:
                if 'prizeName' in data:
                    self._result.append('抽奖成功:{}'.format(data['promptMsg'], data['prizeName']))
                    println('账号:{}, 抽奖成功:{}'.format(self._pt_pin, data['promptMsg'], data['prizeName']))
                else:
                    println('账号:{}, 抽奖成功:{}'.format(self._pt_pin, data['promptMsg']))
                    self._result.append('抽奖成功:{}'.format(data['promptMsg']))
                println('账号:{}, 当前剩余积分:{}'.format(self._pt_pin, data['userScore']))
                self._result.append('当前剩余积分:{}'.format(data['userScore']))

            await self.lottery(session)

        except Exception as e:
            println(e.args)

    async def notify(self):
        """
        消息通知
        :return:
        """
        message = '  账号: {}\n'.format(self._pt_pin)
        for line in self._result:
            message += ''.join(['  ', line, '\n'])

        self._message = message

    async def run(self):
        """
        入口函数
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            task_list = await self.get_task_list(session)

            for j in range(len(task_list)):
                task = task_list[j]
                println('账号: {}, 任务:{}, 进度:{}...'.format(self._pt_pin, task['flexibleData']['taskName'],
                                                         task['flexibleData']['taskProgress']))

                if task['joinTimes'] == task['taskLimit']:
                    self._result.append('任务:{}, 进度:{}...'.format(task['flexibleData']['taskName'],
                                                                 task['flexibleData']['taskProgress']))

                for i in range(task['joinTimes'], task['taskLimit']):
                    println('账号: {}, 去完成{}, 第{}次!'.format(self._pt_pin, task['flexibleData']['taskName'], i + 1))
                    en_award_k = task['enAwardK']
                    await self.do_task(session, en_award_k)

            await self.lottery(session)  # 抽奖

        await self.notify()


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = LuckyTurntable(pt_pin=pt_pin, pt_key=pt_key)
    asyncio.run(app.run())
    # return app.message


if __name__ == '__main__':
    from utils.process import process_start

    process_start(start, name='幸运大转盘')
