#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/21 21:47
# @File    : jd_planting_bean.py
# @Project : jd_scripts
# @Desc    : 种豆得豆
import asyncio
import datetime
import json
import time
from functools import wraps
from urllib.parse import unquote, quote

import aiohttp
import pytz

from pytz import timezone
from datetime import datetime

from utils.notify import push_message_to_tg
from utils.console import println
from utils.logger import logger

from config import JD_COOKIES, USER_AGENT


def println_task(func=None):
    """
    输出任务
    :param func:
    :return:
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        task = args[-1]
        println('开始做{}任务!'.format(task['taskName']))
        res = await func(*args, **kwargs)
        println('已完成{}任务!'.format(task['taskName']))
        return res

    return wrapper


class JdPlantingBean:
    """
    种豆得豆
    """

    headers = {
        "Host": "api.m.jd.com",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "User-Agent": USER_AGENT,
        "Accept-Language": "zh-Hans-CN;q=1,en-CN;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    def __init__(self, pt_pin, pt_key):
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._account = '账号:{}'.format(unquote(pt_pin))
        self._cur_round_id = None  # 本期活动id
        self._prev_round_id = None  # 上期活动id
        self._next_round_id = None  # 下期活动ID
        self._task_list = None  # 任务列表
        self._nickname = None  # 京东昵称
        self._message = ''

    async def post(self, session, function_id, params=None):
        """
        :param session:
        :param function_id:
        :param params:
        :return:
        """
        if params is None:
            params = {}
        params['version'] = '9.2.4.0'
        params['monitor_source'] = 'plant_app_plant_index'
        params['monitor_refer'] = ''

        url = 'https://api.m.jd.com/client.action'

        body = f'functionId={function_id}&body={quote(json.dumps(params))}&appid=ld' \
               f'&client=apple&area=19_1601_50258_51885&build=167490&clientVersion=9.3.2'

        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            logger.info('种豆得豆:{}'.format(text))
            data = json.loads(text)
            return data

        except Exception as e:
            logger.error('{}, 种豆得豆访问服务器失败:[function_id={}], 错误信息:{}'.format(self._account, function_id, e.args))

    async def get(self, session, function_id, body=None):
        """
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        if body is None:
            body = {}

        try:
            body["version"] = "9.2.4.0"
            body["monitor_source"] = "plant_app_plant_index"
            body["monitor_refer"] = ""

            url = f'https://api.m.jd.com/client.action?functionId={function_id}&body={quote(json.dumps(body))}&appid=ld'
            response = await session.get(url=url)
            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            logger.error('{}, 种豆得豆访问服务器失败:[function_id={}], 错误信息:{}'.format(self._account, function_id, e.args))

    async def planting_bean_index(self, session):
        """
        :return:
        """
        data = await self.post(session=session, function_id='plantBeanIndex')

        if not data or data['code'] != '0':
            println('访问种豆得豆首页失败...')
            return
        data = data['data']

        round_list = data['roundList']
        self._prev_round_id = round_list[0]['roundId']
        self._cur_round_id = round_list[1]['roundId']
        self._next_round_id = round_list[2]['roundId']
        self._task_list = data['taskList']
        self._message += f"京东昵称:{data['plantUserInfo']['plantNickName']}\n"
        self._message += f'上期时间:{round_list[0]["dateDesc"].replace("上期 ", "")}\n'
        self._message += f'上期成长值:{round_list[0]["growth"]}'

    async def receive_nutrient(self, session):
        """
        收取营养液
        :param session:
        :return:
        """
        println('开始收取营养液!')
        data = await self.post(session, 'receiveNutrients',
                               {"roundId": self._cur_round_id, "monitor_refer": "plant_receiveNutrients"})
        if 'errorMessage' in data:
            println(data['errorMessage'])

    @println_task
    async def receive_nutrient_task(self, session, task):
        """
        :param session:
        :param task:
        :return:
        """
        params = {
            "monitor_refer": "plant_receiveNutrientsTask",
            "awardType": str(task['taskType'])
        }
        data = await self.get(session, 'receiveNutrientsTask', params)
        println(data)

    @println_task
    async def visit_shop(self, session, task):
        """
        浏览店铺任务
        :param session:
        :param task:
        :return:
        """
        if (int(task['totalNum']) - int(task['gainedNum'])) == 0:
            println('{}任务, 已完成!'.format(task['taskName']))
            return

        shop_data = await self.get(session, 'shopTaskList', {"monitor_refer": "plant_receiveNutrients"})
        if shop_data['code'] != '0':
            println('获取{}任务失败!'.format(task['taskName']))

        shop_list = shop_data['data']['goodShopList'] + shop_data['data']['moreShopList']
        for shop in shop_list:
            body = {
                "monitor_refer": "plant_shopNutrientsTask",
                "shopId": shop["shopId"],
                "shopTaskId": shop["shopTaskId"]
            }
            data = await self.get(session, 'shopNutrientsTask', body)

            if data['code'] == '0' and 'data' in data:
                println(data['data']['nurtToast'])
            else:
                println(data['errorMessage'])

    @println_task
    async def pick_goods_task(self, session, task):
        """
        挑选商品任务
        :return:
        """
        if (int(task['totalNum']) - int(task['gainedNum'])) == 0:
            println('已完成任务{}!'.format(task['taskName']))
            return
        data = await self.get(session, 'productTaskList', {"monitor_refer": "plant_productTaskList"})

        for products in data['data']['productInfoList']:
            for product in products:
                body = {
                    "monitor_refer": "plant_productNutrientsTask",
                    "productTaskId": product['productTaskId'],
                    "skuId": product['skuId']
                }
                res = await self.get(session, 'productNutrientsTask', body)
                if 'errorCode' in res:
                    println(res['errorMessage'])
                else:
                    println(res)

                await asyncio.sleep(0.5)

    @println_task
    async def focus_channel_task(self, session, task):
        """
        关注频道任务
        :param session:
        :param task:
        :return:
        """
        data = await self.get(session, 'plantChannelTaskList')
        if data['code'] != '0':
            println('获取关注频道任务列表失败!')
            return
        data = data['data']
        channel_list = data['goodChannelList'] + data['normalChannelList']

        for channel in channel_list:
            body = {
                "channelId": channel['channelId'],
                "channelTaskId": channel['channelTaskId']
            }
            res = await self.get(session, 'plantChannelNutrientsTask', body)
            println(res)

    async def everyday_gacha(self, session):
        """
        天天扭蛋
        :param session:
        :return:
        """
        data = await self.get(session, 'plantEggLotteryIndex')
        if data['code'] != '0':
            println('查询天天扭蛋机会失败!')
            return

    async def do_tasks(self, session):
        """
        做任务
        :param session:
        :return:
        """
        task_map = {
            1: self.receive_nutrient_task,
            3: self.visit_shop,
            5: self.pick_goods_task,
            10: self.focus_channel_task,
        }
        for task in self._task_list:
            if task['taskType'] not in task_map:
                continue
            await task_map[task['taskType']](session, task)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            await self.planting_bean_index(session)
            # await self.receive_nutrient(session)
            # await self.do_tasks(session)
            await self.everyday_gacha(session)


if __name__ == '__main__':
    for jd_cookie in JD_COOKIES:
        app = JdPlantingBean(jd_cookie['pt_pin'], jd_cookie['pt_key'])
        asyncio.run(app.run())
        break
