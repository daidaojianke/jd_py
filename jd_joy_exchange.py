#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/25 下午8:20 
# @File    : jd_joy_exchange.py
# @Project : jd_scripts
# @Cron    : 56 7,15,23 * * *
# @Desc    : 宠汪汪商品兑换
import random
import time
import asyncio
import aiohttp
import ujson
from dateutil.relativedelta import relativedelta
from jd_joy import JdJoy
from datetime import datetime

from utils.logger import logger
from utils.console import println


class JdJoyExchange(JdJoy):
    """
    宠汪汪兑换京豆
    """

    @logger.catch
    async def exchange_bean(self, session):
        """
        积分换豆
        """
        path = 'gift/getBeanConfigs'
        data = await self.request(session, path)
        if not data:
            println('{}, 获取奖品列表失败!'.format(self.account))
            return

        # 23~6点运行兑换8点场
        if datetime.now().hour >= 23 or datetime.now().hour < 7:  # 0点场
            start_time = datetime.strftime((datetime.now() + relativedelta(days=1)), "%Y-%m-%d 00:00:00")
            key = 'beanConfigs0'
        # 7~15点运行兑换8点场
        elif 7 < datetime.now().hour < 16:  # 8点场
            start_time = datetime.strftime((datetime.now()), "%Y-%m-%d 08:00:00")
            key = 'beanConfigs8'
        # 15~22点运行兑换16点场
        elif 15 < datetime.now().hour < 23:  # 16点场
            start_time = datetime.strftime((datetime.now()), "%Y-%m-%d 16:00:00")
            key = 'beanConfigs16'
        # 其他兑换16点场
        else:  # 默认16点场
            start_time = datetime.now().strftime("%Y-%m-%d 16:00:00")
            key = 'beanConfigs16'

        gift_list = data[key]
        pet_coin = data.get('petCoin')  # 当前积分
        if not pet_coin:
            pet_coin = 0

        println('{}, 当前积分:{}!'.format(self.account, pet_coin))
        gift_id = None
        gift_name = None
        for gift in gift_list:
            # 积分够兑换并且库存大于0
            if pet_coin > gift['salePrice'] and gift['leftStock'] > 0:
                gift_id = gift['id']
                gift_name = gift['giftName']
        if not gift_id:
            println('{}, 当前不满足兑换商品条件!'.format(self.account))
            return

        println('{}, 正在兑换, 商品: {}!'.format(self.account, gift_name))

        exchange_path = 'gift/new/exchange'
        exchange_params = {"buyParam": {"orderSource": 'pet', "saleInfoId": gift_id}, "deviceInfo": {}}

        exchange_start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        exchange_start_timestamp = int(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S")) * 1000)
        delay = random.randint(1, 5) / 10

        while True:
            now = int(time.time()*1000)
            if now + delay * 1000 >= exchange_start_timestamp or now >= exchange_start_timestamp:
                println('{}, 当前时间大于兑换时间, 去兑换:{}'.format(self.account, gift_name))
                break
            else:
                now = datetime.now()
                seconds = int((exchange_start_datetime - now).seconds)
                millisecond = int((exchange_start_datetime - now).seconds * 1000 +
                                  (exchange_start_datetime - now).microseconds / 1000)
                println('{}, 距离兑换开始还有{}秒!'.format(self.account, seconds), millisecond)

                if seconds < 5:
                    timeout = millisecond / 1000
                else:
                    if millisecond - seconds * 1000 > 0:
                        timeout = seconds
                    else:
                        timeout = seconds - 1 + delay

                println('{}, 当前时间小于兑换时间, 等待{}秒!'.format(self.account, timeout))
                await asyncio.sleep(timeout)

        exchange_success = False

        for i in range(10):
            println('{}, 正在尝试第{}次兑换!'.format(self.account, i+1))
            data = await self.request(session, exchange_path, exchange_params, method='POST')
            if data and data['errorCode'] and 'success' in data['errorCode']:
                exchange_success = True
                break
            elif data and data['errorCode'] and 'limit' in data['errorCode']:
                println('{}, 今日已兑换商品:{}!'.format(self.account, gift_name))
                break
            elif data and data['errorCode'] and 'empty' in data['errorCode']:
                println('{}, 奖品:{}已无库存!'.format(self.account, gift_name))
                break
            await asyncio.sleep(0.5)

        if exchange_success:
            println('{}, 成功兑换商品:{}!'.format(self.account, gift_name))
        else:
            println('{}, 无法兑换商品:{}!'.format(self.account, gift_name))

    async def run(self):
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies,
                                         json_serialize=ujson.dumps) as session:
            await self.exchange_bean(session)

        await self.close_browser()


if __name__ == '__main__':
    from utils.process import process_start
    from config import JOY_PROCESS_NUM
    process_start(JdJoyExchange, '宠汪汪兑换', process_num=JOY_PROCESS_NUM)
