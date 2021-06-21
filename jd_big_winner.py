#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/18 6:33 下午
# @File    : jd_big_winner.py
# @Project : jd_scripts
# @Desc    : 省钱大赢家翻翻乐
import asyncio
import json
import time
from urllib.parse import quote
import aiohttp


from config import USER_AGENT
from utils.logger import logger
from utils.console import println
from utils.notify import push_message_to_tg


class BigWinner:
    link_id = 'DA4SkG7NXupA9sksI00L0g'
    ffl_link_id = 'YhCkrVusBVa_O2K-7xE6hA'
    headers = {
        'Host': 'api.m.jd.com',
        'Origin': 'https://openredpacket-jdlite.jd.com',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': USER_AGENT,
        'Referer': 'https://618redpacket.jd.com/withdraw?activityId={}&channel'
                   '=wjicon&lng=&lat=&sid=&un_area='.format(link_id),
        'Accept-Language': 'zh-cn',
    }

    def __init__(self, pt_pin='', pt_key=''):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._pt_pin = pt_pin
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._can_withdraw = False  # 是否可以提现

    async def can_open_reward(self, session):
        """
        判断是否可以开红包
        :return:
        """
        body = {
            'linkId': self.ffl_link_id
        }
        url = 'https://api.m.jd.com/?functionId=gambleHomePage&body={}' \
              '&appid=activities_platform&clientVersion=3.5.0'.format(quote(json.dumps(body)))
        try:
            response = await session.get(url=url)
            data = await response.json()
            logger.info(data)
            if data['code'] != 0:
                logger.info('账号:{}, 无法获取开红包状态: {}'.format(self._pt_pin, data))
            else:
                return data['data']['leftTime'] == 0
        except Exception as e:
            logger.error('判断是否可以开红包失败, 异常信息: {}'.format(e.args))

    async def open_reward(self, session):
        """
        打开红包
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/'
        params = {
            'linkId': self.ffl_link_id,
        }
        body = 'functionId=gambleOpenReward&body={}&t={}&appid=' \
               'activities_platform&clientVersion=3.5.0'.format(quote(json.dumps(params)), int(time.time()*1000))
        session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            logger.info(data)
            if data['code'] == 0:
                println('账号:{}, 开红包成功,获得: {}元红包!'.format(self._pt_pin, data['data']['rewardValue']))
                return data['data']
            elif data['code'] == 20007:
                println('账号:{}, 开红包失败, 今日活动参与次数达到上限!'.format(self._pt_pin))
                return False
            else:
                println('账号:{}, 开红包失败, 原因: {}'.format(self._pt_pin, data))
                return False

        except Exception as e:
            logger.error('翻翻乐开红包失败, 程序出错:{}'.format(e.args))
        return False

    async def doubled_reward(self, session, reward_data):
        """
        翻倍红包
        :return:
        """
        url = 'https://api.m.jd.com/'
        params = {
            'linkId': self.ffl_link_id,
        }
        body = 'functionId=gambleChangeReward&body={}&t={}&appid=' \
               'activities_platform&clientVersion=3.5.0'.format(quote(json.dumps(params)), int(time.time()*1000))
        session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            logger.info(data)
            if data['code'] != 0:
                println('账号:{}, 红包翻倍失败, 原因:{}'.format(self._pt_pin, data['errMsg']))
                return reward_data

            data = data['data']

            if data['rewardState'] == 1:
                if float(data['rewardValue']) > 0.3:
                    self._can_withdraw = True
                    return data
                if data['rewardType'] == 1:
                    println('账号:{}, 第{}次翻倍成功, 获得:{}元红包!'.format(self._pt_pin, data['changeTimes'], data['rewardValue']))
                elif data['rewardType'] == 2:
                    println('账号:{}, 第{}次翻倍成功, 获得:{}元现金!'.format(self._pt_pin, data['changeTimes'], data['rewardValue']))
                else:
                    println('账号:{}, 第{}次翻倍成功, 获得:{}!'.format(self._pt_pin, data['changeTimes'], data))
            elif data['rewardState'] == 3:
                println('账号:{}, 第{}次翻倍 失败，奖品溜走了/(ㄒoㄒ)/~~\n'.format(self._pt_pin, data['changeTimes']))
                return data
            else:
                println('账号:{}, 翻倍成功, 获得:'.format(self._pt_pin, data))

            await asyncio.sleep(0.5)
            return await self.doubled_reward(session, data)

        except Exception as e:
            logger.info('账号:{}, 红包翻倍异常:{}'.format(self._pt_pin, e.args))

    async def withdraw(self, session, reward_data):
        """
        领取现金并提现
        :return:
        """
        url = 'https://api.m.jd.com/'
        params = {
            'linkId': self.ffl_link_id,
            'rewardType': reward_data['rewardType']
        }
        body = 'functionId=gambleObtainReward&body={}&t={}&appid=activities_platform&clientVersion=3.5.0'\
            .format(quote(json.dumps(params)), int(time.time()) * 1000)
        session.headers.add('Content-Type', 'application/x-www-form-urlencoded')

        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            logger.info(data)
            if data['code'] != 0:
                println("账号:{}, 现金领取失败:{}！".format(self._pt_pin, data))
                return
            println("账号:{}, 现金领取成功: {}元现金!".format(self._pt_pin, data['data']['amount']))

            data = data['data']

            withdraw_data = {  # 提现参数
                'businessSource': 'GAMBLE',
                'base': {
                    'id': data['id'],
                    'business': 'redEnvelopeDouble',
                    'poolBaseId': data['poolBaseId'],
                    'prizeGroupId': data['prizeGroupId'],
                    'prizeBaseId': data['prizeBaseId'],
                    'prizeType': data['prizeType']
                },
                'linkId': self.ffl_link_id,
            }
            body = 'functionId=apCashWithDraw&body={}&t={}&appid=activities_platform' \
                   '&clientVersion=3.5.0'.format(quote(json.dumps(withdraw_data)), int(time.time()*1000))
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            logger.info(data)
            println(data)
            if data['code'] == 0:
                push_message_to_tg('账号:{}, 翻翻乐提现成功:{}'.format(self._pt_pin, data['data']))
                println('账号:{}, 提现成功:{}'.format(self._pt_pin, data['data']))
            else:
                push_message_to_tg('账号:{}, 翻翻乐提现成功:{}'.format(self._pt_pin, data['data']))
                println('账号:{}, 提现失败:{}'.format(self._pt_pin, data))
        except Exception as e:
            logger.error('账号:{}, 提现失败, 异常信息:{}'.format(self._pt_pin, e.args))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            can_open_reward = await self.can_open_reward(session)
            if not can_open_reward:
                println("账号:{}, 当前无法开红包, 退出程序...".format(self._pt_pin))
                return

            reward_data = await self.open_reward(session)

            if not reward_data:
                println("账号:{}, 当前无法翻倍红包, 退出程序...".format(self._pt_pin))
                return

            # 可以翻倍红包
            reward_data = await self.doubled_reward(session, reward_data)

            if not self._can_withdraw:
                print('账号:{}, 当前无法提取现金, 退出程序...'.format(self._pt_pin))
                return

            await asyncio.sleep(0.5)
            # 可以提现
            await self.withdraw(session, reward_data)


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = BigWinner(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from utils.process import process_start
    process_start(start, '翻翻乐')
