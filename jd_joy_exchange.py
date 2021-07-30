#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/25 下午8:20 
# @File    : jd_joy_exchange.py
# @Project : jd_scripts 
# @Desc    : 宠汪汪商品兑换
import asyncio
import aiohttp
import ujson
from dateutil.relativedelta import relativedelta

from jd_joy import JdJoy
from datetime import datetime

from utils.console import println


class JdJoyExchange(JdJoy):
    """
    宠汪汪兑换京豆
    """
    def __init__(self, pt_pin, pt_key):
        super(JdJoyExchange, self).__init__(pt_pin, pt_key)

    async def exchange_bean(self, session):
        """
        积分换豆
        """
        path = 'gift/getBeanConfigs'
        data = await self.request(session, path)
        if not data:
            println('{}, 获取奖品列表失败!'.format(self._pt_pin))
            return

        # 23~6点运行兑换8点场
        if datetime.now().hour >= 23 or datetime.now().hour < 7:  # 0点场
            start_time = datetime.strftime((datetime.now() + relativedelta(days=1)), "%Y-%m-%d 00:00:00")
            key = 'beanConfigs0'
        # 7~14点运行兑换16点场
        elif datetime.now().hour > 7 or datetime.now().hour < 15:  # 8点场
            start_time = datetime.strftime((datetime.now()), "%Y-%m-%d 08:00:00")
            key = 'beanConfigs8'
        # 15~22点运行兑换16点场
        elif datetime.now().hour > 15 or 16 < datetime.now().hour < 23:  # 16点场
            start_time = datetime.strftime((datetime.now()), "%Y-%m-%d 16:00:00")
            key = 'beanConfigs16'
        # 其他兑换16点场
        else:  # 默认16点场
            start_time = datetime.now().strftime("%Y-%m-%d 16:00:00")
            key = 'beanConfigs16'

        gift_list = data[key]
        pet_coin = data['petCoin']  # 当前积分
        gift_id = None
        gift_name = None
        for gift in gift_list:
            if pet_coin > gift['salePrice']:
                gift_id = gift['id']
                gift_name = gift['giftName']
        if not gift_id:
            println('{}, 当前不满足兑换商品条件!'.format(self._pt_pin))
            return

        println('{}, 正在兑换, 商品: {}!'.format(self._pt_pin, gift_name))

        exchange_path = 'gift/new/exchange'
        exchange_params = {"buyParam": {"orderSource": 'pet', "saleInfoId": gift_id}, "deviceInfo": {}}

        while True:
            now = datetime.now()
            nx_start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if now >= nx_start_time:
                println('{}, 当前时间大于兑换时间, 去兑换:{}'.format(self._pt_pin, gift_name))
                break
            else:
                remain_seconds = int((now - nx_start_time).total_seconds())
                if remain_seconds < 10:
                    timeout = 1
                else:
                    timeout = abs(remain_seconds) - 1

                    # 防止兑换的时候需要验证码，尝试先触发验证码
                    path = 'gift/getBeanConfigs'
                    await self.request(session, path)
                println('{}, 当前时间小于兑换时间, 等待{}秒!'.format(self._pt_pin, timeout))
                await asyncio.sleep(timeout)

        exchange_success = False

        for i in range(10):
            data = await self.request(session, exchange_path, exchange_params, method='POST')
            if data and data['errorCode'] and 'success' in data['errorCode']:
                exchange_success = True
                break
            elif data and data['errorCode'] and 'limit' in data['errorCode']:
                println('{}, 今日已兑换商品:{}!'.format(self._pt_pin, gift_name))
                return
            await asyncio.sleep(0.1)

        if exchange_success:
            println('{}, 成功兑换商品:{}!'.format(self._pt_pin, gift_name))
        else:
            println('{}, 无法兑换商品:{}!'.format(self._pt_pin, gift_name))

    async def run(self):
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._aiohttp_cookies,
                                         json_serialize=ujson.dumps) as session:
            await self.exchange_bean(session)

        await self.close_browser()


def start(pt_pin, pt_key, name='宠汪汪兑换'):
    """
    宠汪汪商品兑换
    """
    try:
        app = JdJoyExchange(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    from utils.process import process_start
    from config import JOY_PROCESS_NUM
    process_start(start, '宠汪汪兑换', process_num=JOY_PROCESS_NUM)
