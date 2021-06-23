#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/23 9:41 上午
# @File    : jd_shark_bean.py
# @Project : jd_scripts
# @Desc    : 京东APP->我的->签到领豆->摇金豆
import asyncio
import time
import aiohttp
import json
from urllib.parse import quote, unquote, urlencode

from utils.logger import logger
from utils.console import println
from utils.notify import push_message_to_tg

from config import JD_COOKIES, USER_AGENT


class JdSharkBean:
    """
    摇金豆
    """
    headers = {
        'origin': 'https://spa.jd.com',
        'user-agent': USER_AGENT,
        'referer': 'https://spa.jd.com/home?source=JingDou',
        'accept': 'application/json'
    }

    METHOD_GET = 'get'
    METHOD_POST = 'post'

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._nickname = None
        self._sign_info = {}
        self._bean_count = 0
        self._red_packet_num = 0
        self._pt_pin = unquote(pt_pin)

    async def request(self, session, params=None, method='get'):
        """
        get 请求
        :param params:
        :param method:
        :param session:
        :return:
        """
        if params is None:
            params = {}

        url = 'https://api.m.jd.com/?{}'.format(urlencode(params))

        try:
            if method == self.METHOD_POST:
                response = await session.post(url)
            else:
                response = await session.get(url)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            logger.add(e.args)

    async def get_index_data(self, session):
        """
        获取首页数据
        :param session:
        :return:
        """
        params = {
            't': int(time.time()*1000),
            'functionId': 'pg_channel_page_data',
            'appid': 'sharkBean',
            'body': {"paramData": {"token": "dd2fb032-9fa3-493b-8cd0-0d57cd51812d"}}
        }
        println('{}, 正在登录首页...'.format(self._pt_pin))
        data = await self.request(session, params, self.METHOD_GET)
        return data

    async def daily_sign(self, session):
        """
        每日签到
        :param session:
        :return:
        """
        data = await self.get_index_data(session)
        if 'data' not in data or 'floorInfoList' not in data['data']:
            println('{}, 无法获取签到数据:{}'.format(self._pt_pin, data))
            return

        sign_info = None

        for floor_info in data['data']['floorInfoList']:
            if 'code' in floor_info and floor_info['code'] == 'SIGN_ACT_INFO':
                cursor = floor_info['floorData']['signActInfo']['currSignCursor']
                token = floor_info['token']
                sign_info = {
                    'status': '',
                    'body': {
                        "floorToken": token,
                        "dataSourceCode": "signIn",
                        "argMap": {
                            "currSignCursor": cursor
                        }
                    }
                }
                for item in floor_info['floorData']['signActInfo']['signActCycles']:
                    if item['signCursor'] == cursor:
                        sign_info['status'] = item['signStatus']

        if not sign_info:
            println('{}, 查找签到数据失败, 无法签到！'.format(self._pt_pin))
            return

        if sign_info['status'] != -1:
            println('{}, 当前状态无法签到, 可能已签到过!'.format(self._pt_pin))
            return

        # 签到参数
        sign_params = {
            't': int(time.time() * 1000),
            'functionId': 'pg_interact_interface_invoke',
            'appid': 'sharkBean',
            'body': sign_info['body'],
        }

        res = await self.request(session,  sign_params, self.METHOD_POST)
        if 'success' in res and res['success']:
            println('{}, 签到成功!'.format(self._pt_pin))
            for reward in res['data']['rewardVos']:
                if reward['jingBeanVo'] is not None:
                    self._bean_count += int(reward['jingBeanVo']['beanNum'])
                if reward['hongBaoVo'] is not None:
                    self._red_packet_num = float(self._red_packet_num) + float(reward['hongBaoVo'])
        else:
            println('{}, 签到失败!'.format(self._pt_pin))

    async def notify(self):
        """
        :return:
        """
        message = '\n【活动名称】摇金豆\n【用户ID】{}\n【获得金豆】{}\n【获得红包】{}\n\n'.format(self._pt_pin,
                                                                        self._bean_count, self._red_packet_num)
        push_message_to_tg(message)
        println(message)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            await self.daily_sign(session)

        await self.notify()


def start(pt_pin, pt_key):
    """
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdSharkBean(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    pin, key = JD_COOKIES[0].values()
    start(pin, key)
