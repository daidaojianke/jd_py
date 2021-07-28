#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/28 2:06 下午
# @File    : dj_base.py
# @Project : jd_scripts
# @Desc    :
import json
import time
import math
import random
import asyncio

from urllib.parse import unquote, urlencode
from config import USER_AGENT
from utils.console import println


def uuid():
    """
    生成设备ID
    :return:
    """

    def s4():
        return hex(math.floor((1 + random.random()) * 0x10000))[3:]

    return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4()


class DjBase:
    headers = {
        'user-agent': USER_AGENT,
        'origin': 'https://daojia.jd.com',
        'referer': 'https://daojia.jd.com/taro2orchard/h5dist/',
        'content-type': 'application/x-www-form-urlencoded',
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self.lat = '23.' + str(math.floor(random.random() * (99999 - 10000) + 10000))
        self.lng = '113.' + str(math.floor(random.random() * (99999 - 10000) + 10000))
        self.city_id = str(math.floor(random.random() * (1500 - 1000) + 1000))
        self.device_id = uuid()
        self.trace_id = self.device_id + str(int(time.time() * 1000))
        self.nickname = None
        self.pin = pt_pin
        self.account = unquote(self.pin)
        self.dj_pin = None

        self.cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
            'deviceid_pdj_jd': self.device_id
        }

        self.message = None

    async def request(self, session, function_id='', body=None, method='GET'):
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
                '_jdrandom': int(time.time() * 1000),
                '_funid_': function_id,
                'functionId': function_id,
                'body': json.dumps(body),
                'tranceId': self.trace_id,
                'deviceToken': self.device_id,
                'deviceId': self.device_id,
                'deviceModel': 'appmodel',
                'appName': 'paidaojia',
                'appVersion': '6.6.0',
                'platCode': 'h5',
                'platform': '6.6.0',
                'channel': 'h5',
                'city_id': self.city_id,
                'lng_pos': self.lng,
                'lat_pos': self.lat,
                'lng': self.lng,
                'lat': self.lat,
                'isNeedDealError': 'true',
            }

            if function_id == 'xapp/loginByPtKeyNew':
                params['code'] = '011UYn000apwmL1nWB000aGiv74UYn03'

            if method == 'GET':
                url = 'https://daojia.jd.com/client?' + urlencode(params)
                response = await session.get(url=url)
            else:
                params['method'] = 'POST'
                url = 'https://daojia.jd.com/client?' + urlencode(params)
                response = await session.post(url=url)

            text = await response.text()
            data = json.loads(text)

            # 所有API等待1s, 避免操作繁忙
            await asyncio.sleep(1)

            return data
        except Exception as e:
            println('{}, 无法获取服务器数据, {}!'.format(self.account, e.args))
            return None

    async def get(self, session, function_id, body=None):
        """
        get 方法
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        return await self.request(session, function_id, body, method='GET')

    async def post(self, session, function_id, body=None):
        """
        post 方法
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        return await self.request(session, function_id, body, method='POST')

    async def login(self, session):
        """
        用京东APP获取京东到家APP的cookies
        :return:
        """
        println('{}, 正在登录京东到家!'.format(self.account))
        body = {"fromSource": 5, "businessChannel": 150, "subChannel": "", "regChannel": ""}
        res = await self.get(session, 'xapp/loginByPtKeyNew', body)
        if res['code'] != '0':
            println('{}, 登录失败, 退出程序!'.format(self.account))
            return False
        if 'nickname' in res['result']:
            self.nickname = res['result']['nickname']
        else:
            self.nickname = self.account

        self.dj_pin = res['result']['PDJ_H5_PIN']

        cookies = {
            'o2o_m_h5_sid': res['result']['o2o_m_h5_sid'],
            'deviceid_pdj_jd': self.device_id,
            'PDJ_H5_PIN': res['result']['PDJ_H5_PIN'],
        }
        return cookies

    async def finish_task(self, session, task_name, body):
        """
        完成任务
        :param body:
        :param task_name:
        :param session:
        :return:
        """
        res = await self.get(session, 'task/finished', body)
        if res['code'] != '0':
            println('{}, 无法完成任务:《{}》!'.format(self.account, task_name))
        else:
            println('{}, 成功完成任务:《{}》!'.format(self.account, task_name))

    async def receive_task(self, session, task):
        """
        领取任务
        :param session:
        :param task:
        :param body:
        :return:
        """
        task_name = task['taskName']
        if task['status']:
            println('{}, 任务:《{}》已领取!'.format(self.account, task_name))
            return

        body = {
            "modelId": task['modelId'],
            "taskId": task['taskId'],
            "taskType": task['taskType'],
            "plateCode": 3
        }

        res = await self.get(session, 'task/received', body)
        if res['code'] != '0':
            println('{}, 无法领取任务:《{}》！'.format(self.account, task_name))
        else:
            println('{}, 成功领取任务:《{}》!'.format(self.account, task_name))

    async def browse_task(self, session, task):
        """
        浏览任务
        :param session:
        :param task:
        :return:
        """
        body = {
            "modelId": task['modelId'],
            "taskId": task['taskId'],
            "taskType": task['taskType'],
            "plateCode": 3,
        }
        if task['status'] == 0:  # 任务状态0: 待领取, 1待完成, 2待领奖, 3完成
            await self.receive_task(session, task)
        await asyncio.sleep(1)
        await self.finish_task(session, task['taskName'], body)

    async def get_task_award(self, session, task):
        """
        获取任务奖励水滴
        :param task:
        :param session:
        :return:
        """
        body = {
            "modelId": task['modelId'],
            "taskId": task['taskId'],
            "taskType": task['taskType'],
            "plateCode": 4
        }
        res = await self.get(session, 'task/sendPrize', body)
        if res['code'] != '0':
            println('{}, 无法领取任务:《{}》奖励!'.format(self.account, task['taskName']))
        else:
            println('{}, 成功领取任务: 《{}》奖励!'.format(self.account, task['taskName']))
