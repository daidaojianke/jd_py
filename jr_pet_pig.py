#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:18 下午
# @File    : jr_pet_pig.py
# @Project : jd_scripts
# @Desc    : 京东金融->养猪猪
import json
import time

import aiohttp
import asyncio

from urllib.parse import unquote, quote

from furl import furl

from utils.process import process_start
from utils.console import println
from utils.notify import notify
from config import USER_AGENT


class JrPetPig:
    """
    养猪猪
    """

    headers = {
        'accept': 'application/json',
        'origin': 'https://u.jr.jd.com',
        'user-agent': USER_AGENT,
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'referer': 'https://u.jr.jd.com/uc-fe-wxgrowing/cloudpig/index/'
    }

    def __init__(self, pt_pin, pt_key):

        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._pt_pin = unquote(pt_pin)
        self._host = 'https://ms.jr.jd.com/gw/generic/uc/h5/m/'

    async def login(self, session):
        """
        :return:
        """
        url = self._host + 'pigPetLogin?_={}'.format(int(time.time()))
        body = 'reqData={}'.format(quote(json.dumps(
            {
                "source": 2,
                "channelLV": "juheye",
                "riskDeviceParam": "{}",
            }
        )))
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            if data['resultCode'] != 0 or data['resultData']['resultCode'] != 0:
                println('{}, 登录失败, {}'.format(self._pt_pin, data))
                return False
            if 'hasPig' not in data['resultData']['resultData'] or not data['resultData']['resultData']['hasPig']:
                println('{}, 未开启养猪猪活动, 请前往京东金融APP开启!'.format(self._pt_pin))
                return False
            return True
        except Exception as e:
            println('{}, 登录失败, {}'.format(self._pt_pin, e.args))
            return False

    async def sign(self, session):
        """
        签到
        :param session:
        :return:
        """
        try:
            url = self._host + 'pigPetSignIndex?_={}'.format(int(time.time() * 1000))
            body = 'reqData={}'.format(quote(json.dumps({"source": 0, "channelLV": "", "riskDeviceParam": "{}"})))
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            sign_list = data['resultData']['resultData']['signList']
            today = data['resultData']['resultData']['today']
            for sign_item in sign_list:
                if sign_item['no'] != today:
                    continue

                # 找到今天的签到数据
                if sign_item['status'] != 0:
                    println('{}, 今日已签到!'.format(self._pt_pin))
                    break

                sign_url = self._host + 'pigPetSignOne?_={}'.format(int(time.time() * 1000))
                body = 'reqData={}'.format(quote(json.dumps({"source": 0, "no": sign_item['no'],
                                                             "channelLV": "", "riskDeviceParam": "{}"})))
                response = await session.post(url=sign_url, data=body)
                text = await response.text()
                data = json.loads(text)
                if data['resultCode'] == 0:
                    println('{}, 签到成功!'.format(self._pt_pin))
                else:
                    println('{}, 签到失败, {}'.format(self._pt_pin, data['resultMsg']))
                break

        except Exception as e:
            println('{}, 签到失败, 异常:{}'.format(self._pt_pin, e.args))

    async def open_box(self, session):
        """
        开宝箱
        :param session:
        :return:
        """
        url = self._host + 'pigPetOpenBox?_={}'.format(int(time.time() * 1000))
        body = 'reqData={}'.format(quote(json.dumps({
            "source": 0, "channelLV": "yqs", "riskDeviceParam": "{}", "no": 5,
            "category": "1001", "t": int(time.time() * 1000)
        })))
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            if data['resultData']['resultCode'] != 0:
                println('{}, {}!'.format(self._pt_pin, data['resultData']['resultMsg']))
                return
            if 'award' not in data['resultData']['resultData']:
                return
            content = data['resultData']['resultData']['award']['content']
            count = data['resultData']['resultData']['award']['count']
            println('{}, 开宝箱获得:{}, 数量:{}'.format(self._pt_pin, content, count))
            await asyncio.sleep(1)
            await self.open_box(session)
        except Exception as e:
            println('{}, 开宝箱失败, {}'.format(self._pt_pin, e.args))

    async def lottery(self, session):
        """
        抽奖
        :param session:
        :return:
        """
        url = self._host + 'pigPetLotteryIndex?_={}'.format(int(time.time() * 1000))
        body = 'reqData={}'.format(quote(json.dumps({
            "source": 0,
            "channelLV": "juheye",
            "riskDeviceParam": "{}"
        })))
        try:
            response = await session.post(url, data=body)
            text = await response.text()
            data = json.loads(text)
            lottery_count = data['resultData']['resultData']['currentCount']
            if lottery_count < 1:
                println('{}, 暂无抽奖次数!'.format(self._pt_pin))
                return

            lottery_url = self._host + 'pigPetLotteryPlay?_={}'.format(int(time.time() * 1000))
            body = 'reqData={}'.format(quote(json.dumps({
                "source": 0,
                "channelLV": "juheye",
                "riskDeviceParam": "{}",
                "t": int(time.time() * 1000),
                "type": 0,
            })))

            for i in range(lottery_count):
                response = await session.post(url=lottery_url, data=body)
                text = await response.text()
                data = json.loads(text)
                if data['resultData']['resultCode'] == 0:
                    println('{}, 抽奖成功!'.format(self._pt_pin))
                else:
                    println('{}, 抽奖失败!'.format(self._pt_pin))

        except Exception as e:
            println('{}, 抽奖失败, {}'.format(self._pt_pin, e.args))

    async def do_mission(self, session, mission):
        """
        做任务
        :return:
        """
        try:
            mission_id = mission['mid'].replace('MC', '')
            res = await self.request_mission(session, 'queryMissionReceiveAfterStatus',
                                             {"missionId": mission_id})
            if not res or res['resultCode'] != 0 or res['resultData']['code'] != '0000':
                return False

            # 任务URL带有readTime的表示需要等待N秒, 没有则等待一秒, 防止频繁访问出错
            t = int(furl(mission['url']).args.get('readTime', 0))

            if t == 0:  # 非浏览任务做不了
                return False

            println('{}, 正在做任务:{}, 需要等待{}S.'.format(self._pt_pin, mission['missionName'], t))

            await asyncio.sleep(int(t))

            res = await self.request_mission(session, 'finishReadMission', {"missionId": str(mission_id),
                                                                            "readTime": t})
            if not res or res['resultCode'] != 0 or res['resultData']['code'] != '0000':
                return False
            return True

        except Exception as e:
            println(e.args)
            return False

    async def receive_or_finish_mission(self, session, mission):
        """
        领取任务或完成任务!
        :param mission:
        :param session:
        :param mid:
        :return:
        """
        try:
            mission_url = self._host + 'pigPetDoMission?_='.format(int(time.time() * 1000))
            body = 'reqData={}'.format(quote(json.dumps({
                "source": 0,
                "channelLV": "",
                "riskDeviceParam": "{}",
                "mid": mission['mid']
            })))
            response = await session.post(url=mission_url, data=body)
            text = await response.text()
            data = json.loads(text)
            return data['resultData']
        except Exception as e:
            println(e.args)

    async def request_mission(self, session, function_id, body):
        """
        :param session:
        :param function_id:
        :param body:
        :return:
        """
        try:
            url = 'https://ms.jr.jd.com/gw/generic/mission/h5/m/{}?reqData={}'.format(function_id,
                                                                                      quote(json.dumps(body)))
            response = await session.get(url=url)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            println("{}, 访问服务器异常, 信息:{}".format(self._pt_pin, e.args))

    async def missions(self, session):
        """
        做任务
        :param session:
        :return:
        """
        url = self._host + 'pigPetMissionList?_={}'.format(int(time.time() * 1000))
        body = 'reqData={}'.format(quote(json.dumps({
            "source": 0,
            "channelLV": "",
            "riskDeviceParam": "{}"
        })))
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            mission_list = data['resultData']['resultData']['missions']
            for mission in mission_list:
                if mission['status'] == 5:
                    println('{}, 任务:{}, 今日已完成!'.format(self._pt_pin, mission['missionName']))
                    continue
                if mission['status'] == 4:
                    data = await self.receive_or_finish_mission(session, mission)
                    if data['resultCode'] == 0:
                        println('{}, 成功领取任务:{}的奖励!'.format(self._pt_pin, mission['missionName']))
                    else:
                        println('{}, 领取任务:{}奖励失败!'.format(self._pt_pin, mission['missionName']))

                if mission['status'] == 3:
                    await self.receive_or_finish_mission(session, mission)
                    await asyncio.sleep(0.5)
                    success = await self.do_mission(session, mission)
                    if not success:
                        continue
                    await asyncio.sleep(1)
                    data = await self.receive_or_finish_mission(session, mission)
                    await asyncio.sleep(0.5)
                    if data['resultCode'] == 0:
                        println('{}, 成功领取任务:{}的奖励!'.format(self._pt_pin, mission['missionName']))
                    else:
                        println('{}, 领取任务:{}奖励失败!'.format(self._pt_pin, mission['missionName']))

        except Exception as e:
            println("{}, 获取任务列表失败!".format(e.args))

    async def add_food(self, session):
        """
        喂猪
        :return:
        """
        url = self._host + 'pigPetUserBag?_={}'.format(int(time.time()))
        body = 'reqData={}'.format(quote(json.dumps(
            {"source": 0, "channelLV": "yqs", "riskDeviceParam": "{}", "t": int(time.time()*1000), "skuId": "1001003004",
             "category": "1001"})))
        try:
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            if data['resultCode'] != 0 or data['resultData']['resultCode'] != 0:
                println("{}, 查询背包信息失败, 无法喂猪!".format(self._pt_pin))
                return
            goods_list = data['resultData']['resultData']['goods']

            for goods in goods_list:
                if goods['count'] < 20:  # 大于20个才能喂猪
                    continue
                times = int(goods['count'] / 20)  # 可喂猪次数
                url = self._host + 'pigPetAddFood?_={}'.format(int(time.time()))
                body = 'reqData={}'.format(quote(json.dumps({
                    "source": 0,
                    "channelLV": "yqs",
                    "riskDeviceParam": "{}",
                    "skuId": str(goods['sku']),
                    "category": "1001",
                })))
                for i in range(times):
                    response = await session.post(url=url, data=body)
                    text = await response.text()
                    data = json.loads(text)
                    if data['resultCode'] == 0 and data['resultData']['resultCode'] == 0:
                        println('{}, 成功投喂20个{}'.format(self._pt_pin, goods['goodsName']))
                        println('{}, 等待10s后进行下一次喂猪!'.format(self._pt_pin))
                        await asyncio.sleep(10)
                    else:
                        println('{}, 投喂20个{}失败!'.format(self._pt_pin, goods['goodsName']))
            println('{}, 食物已消耗完, 结束喂猪!'.format(self._pt_pin))
        except Exception as e:
            println('喂猪失败!异常:{}'.format(e.args))

    async def run(self):
        """
        入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            is_login = await self.login(session)
            if not is_login:
                println('{},登录失败, 退出程序...'.format(self._pt_pin))
                return
            await self.sign(session)
            await self.missions(session)
            await self.open_box(session)
            await self.lottery(session)
            await self.add_food(session)
            await self.notify(session)

    async def notify(self, session):
        """
        通知
        :return:
        """
        try:
            await asyncio.sleep(1)  # 避免查询失败
            url = self._host + 'pigPetLogin?_={}'.format(int(time.time()))
            body = 'reqData={}'.format(quote(json.dumps({
                "source": 2,
                "channelLV": "juheye",
                "riskDeviceParam": "{}",
            })))
            response = await session.post(url=url, data=body)
            text = await response.text()
            data = json.loads(text)
            curr_level_count = data['resultData']['resultData']['cote']['pig']['currLevelCount']  # 当前等级需要喂养的次数
            curr_count = data['resultData']['resultData']['cote']['pig']['currCount']   # 当前等级已喂猪的次数
            curr_level = data['resultData']['resultData']['cote']['pig']['curLevel']
            curr_level_message = '成年期' if curr_level == 3 else '哺乳期'
            pig_id = data['resultData']['resultData']['cote']['pig']['pigId']
            await asyncio.sleep(1)
            wish_url = self._host + 'pigPetMyWish1?_={}'.format(int(time.time()))
            body = 'reqData={}'.format(quote(json.dumps({
                "pigId": pig_id,
                "channelLV": "",
                "source": 0,
                "riskDeviceParam": "{}"})))
            response = await session.post(url=wish_url, data=body)
            text = await response.text()
            data = json.loads(text)
            award_name = data['resultData']['resultData']['award']['name']
            award_tips = data['resultData']['resultData']['award']['content']
            message = '\n【活动名称】{}\n【用户ID】{}\n【奖品名称】{}\n【完成进度】{}\n【小提示】{}'.format(
                '京东金融养猪猪', self._pt_pin, award_name, '{}:{}/{}'.format(curr_level_message, curr_count, curr_level_count), award_tips
            )
            println(message)
        except Exception as e:
            println(e.args)


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JrPetPig(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    process_start(start, '养猪猪')
