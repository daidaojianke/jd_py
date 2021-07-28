#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/27 2:00 下午
# @File    : dj_fruit.py
# @Project : jd_scripts
# @Desc    : 京东APP->京东到家->领免费水果
import aiohttp
import math
import json
import time
import random
import asyncio
import base64
from utils.console import println
from urllib.parse import unquote, urlencode
from config import USER_AGENT, DJ_FRUIT_CODE, DJ_FRUIT_KEEP_WATER


def uuid():
    """
    生成设备ID
    :return:
    """

    def s4():
        return hex(math.floor((1 + random.random()) * 10000))[2:]

    return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4()


class DjFruit:
    """
    京东到家领水果
    """
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

        self._lat = '30.' + str(math.floor(random.random() * (99999 - 10000) + 10000))
        self._lng = '114.' + str(math.floor(random.random() * (99999 - 10000) + 10000))
        self._city_id = str(math.floor(random.random() * (1500 - 1000) + 1000))
        self._device_id = uuid()
        self._trance_id = self._device_id + str(int(time.time() * 1000))
        self._nickname = None
        self._pin = pt_pin
        self._account = unquote(self._pin)
        self._dj_pin = None

        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
            'deviceid_pdj_jd': self._device_id
        }

        self._message = None

    @property
    def message(self):
        return self._message

    async def request(self, session, function_id='', body=None, method='GET'):
        """
        请求数据
        :param session:
        :param function_id:
        :param body:
        :param params:
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
                'tranceId': self._trance_id,
                'deviceToken': self._device_id,
                'deviceId': self._device_id,
                'deviceModel': 'appmodel',
                'appName': 'paidaojia',
                'appVersion': '6.6.0',
                'platCode': 'h5',
                'platform': '6.6.0',
                'channel': 'h5',
                'city_id': self._city_id,
                'lng_pos': self._lng,
                'lat_pos': self._lat,
                'lng': self._lng,
                'lat': self._lat,
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
            println('{}, 无法获取服务器数据, {}!'.format(self._account, e.args))
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
        println('{}, 正在登录到家果园!'.format(self._account))
        body = {"fromSource": 5, "businessChannel": 150, "subChannel": "", "regChannel": ""}
        res = await self.get(session, 'xapp/loginByPtKeyNew', body)
        if res['code'] != '0':
            println('{}, 登录失败, 退出程序!'.format(self._account))
            return False
        if 'nickname' in res['result']:
            self._nickname = res['result']['nickname']
        else:
            self._nickname = self._account

        self._dj_pin = res['result']['PDJ_H5_PIN']

        cookies = {
            'pt_pin': self._cookies['pt_pin'],
            'pt_key': self._cookies['pt_key'],
            'o2o_m_h5_sid': res['result']['o2o_m_h5_sid'],
            'deviceid_pdj_jd': self._device_id,
            'PDJ_H5_PIN': res['result']['PDJ_H5_PIN'],
            'PDJ_H5_JDPIN': res['result']['PDJ_H5_JDPIN']
        }
        return cookies

    async def finish_task(self, session, task_name, body):
        """
        完成任务
        :param body:
        :param task_name:
        :param session:
        :param task:
        :return:
        """
        res = await self.get(session, 'task/finished', body)
        if res['code'] != '0':
            println('{}, 无法完成任务:《{}》!'.format(self._account, task_name))
        else:
            println('{}, 成功完成任务:《{}》!'.format(self._account, task_name))

    async def receive_task(self, session, task_name, body):
        """
        领取任务
        :param session:
        :param task_name:
        :param body:
        :return:
        """
        res = await self.get(session, 'task/received', body)
        if res['code'] != '0':
            println('{}, 无法领取任务:《{}》！'.format(self._account, task_name))
        else:
            println('{}, 成功领取任务:《{}》!'.format(self._account, task_name))

    async def daily_water_award(self, session, task):
        """
        每日水滴奖励
        :param task:
        :param session:
        :return:
        """
        body = {
            "modelId": task['modelId'],
            "taskId": task['taskId'],
            "taskType": task['taskType'],
            "plateCode": 3,
            "subNode": ''
        }
        await self.finish_task(session, task['taskName'], body)

    async def daily_sign(self, session, task):
        """
        每日签到
        :param session:
        :param task:
        :return:
        """

        if task['todayFinishNum'] > 0:
            println('{}, 今日已签到!'.format(self._account))
            return

        sub_node = 'null'

        for item in task['subList']:
            if item['sendStatus'] == 0:
                sub_node = item['node']
                break

        body = {
            "modelId": task['modelId'],
            "taskId": task['taskId'],
            "taskType": task['taskType'],
            "plateCode": 3,
            "subNode": sub_node
        }
        await self.finish_task(session, task['taskName'], body)

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
        await self.receive_task(session, task['taskName'], body)
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
            println('{}, 无法领取任务:《{}》奖励!'.format(self._account, task['taskName']))
        else:
            println('{}, 成功领取任务: 《{}》奖励!'.format(self._account, task['taskName']))

    async def receive_water(self, session, task):
        """
        定时领水滴
        :param session:
        :param task:
        :return:
        """
        pass

    async def watering(self, session, times=None, batch=True, keep_water=10):
        """
        浇水
        :param times: 浇水次数
        :param session:
        :param batch: 是否批量浇水
        :param keep_water: 保留水滴
        :return:
        """
        water_info = await self.get_water_info(session)
        if not water_info:
            println('{}, 无法获取用户水滴信息!'.format(self._account))
            return

        water_balance = water_info['userWaterBalance']
        if not times:
            times = int((water_balance - keep_water) / 10)

        if water_balance - times * 10 < keep_water:
            println('{}, 执行完浇水, 剩余水滴将小于保留水滴:{}g, 故不浇水!'.format(self._account, keep_water))
            return

        if water_balance < times * 10:
            println('{}, 当前水滴:{}, 不够浇{}次水, 不浇水...'.format(self._account, water_balance, times))
            return

        if times < 1:
            println('{}, 当前不需要浇水!'.format(self._account))
            return

        println('{}, 当前水滴:{}, 需要浇水:{}次!'.format(self._account, water_balance, times))

        if batch:
            res = await self.post(session, 'fruit/watering', {"waterTime": times})
            if res['code'] != '0':
                println('{}, {}次浇水失败!'.format(self._account, times))
            else:
                println('{}, 成功浇水{}次!'.format(self._account, times))
            return

        for i in range(1, times + 1):
            res = await self.post(session, 'fruit/watering', {"waterTime": 1})
            if res['code'] != '0':
                println('{}, 第{}次浇水失败, 不再浇水!'.format(self._account, i))
                break
            else:
                println('{}, 第{}次浇水成功!'.format(self._account, i))

    async def receive_water_red_packet(self, session):
        """
        领取浇水红包
        :param session:
        :return:
        """
        res = await self.get(session, 'fruit/getWaterRedPackInfo')
        if res['code'] != '0' or 'result' not in res:
            println('{}, 查询浇水红包信息失败!'.format(self._account))
            return

        rest_progress = float(res['result']['restProgress'])

        if rest_progress > 0.0:
            println('{}, 浇水红包差{}可以打开!'.format(self._account, rest_progress))
            return

        res = await self.get(session, 'fruit/receiveWaterRedPack')
        if res['code'] != '0':
            println('{}, 打开浇水红包失败!'.format(self._account))
        else:
            println('{}, 成功打开浇水红包!'.format(self._account))

    async def receive_water_bottle(self, session):
        """
        领取水瓶
        :param session:
        :return:
        """
        res = await self.get(session, 'fruit/receiveWaterBottle')
        if res['code'] != '0':
            println('{}, 领取水瓶水滴失败!'.format(self._account))
        else:
            println('{}, 成功领水瓶水滴!'.format(self._account))

    async def do_task(self, session):
        """
        做任务
        :param session:
        :return:
        """
        res = await self.get(session, 'task/list', {"modelId": "M10007", "plateCode": 3})

        if res['code'] != '0':
            println('{}, 获取任务列表失败!'.format(self._account))
            return

        data = res['result']
        task_list = data['taskInfoList']

        for i in range(len(task_list)):
            task = task_list[i]
            task_name = task['taskName']
            task_type = task['taskType']

            if task_type in [506, 513]:  # 下单奖励, 超级多单任务
                println('{}, 任务:《{}》无法完成, 请手动执行!'.format(self._account, task_name))
                continue

            if task['status'] == 3:  # 任务完成并且领取了水滴
                println('{}, 任务:《{}》今日已完成!'.format(self._account, task_name))
                continue

            if task['status'] == 2:  # 任务完成，但未领水滴
                await self.get_task_award(session, task)
                continue

            if task_type == 1101:  # 签到任务
                await self.daily_sign(session, task)
            elif task_type == 1102:  # 定时领水滴
                await self.finish_task(session, task_name, {"modelId": task['modelId'], "taskId": task['taskId'],
                                                            "taskType": task['taskType'], "plateCode": 3})
            elif task_type == 1103:  # 每日领水滴
                await self.daily_water_award(session, task)
            elif task_type in [307, 310, 901]:  # 浏览类型任务
                await self.browse_task(session, task)
                await self.get_task_award(session, task)
            elif task_type == 1104:  # 邀请好友领水果
                pass
            elif task_type == [502, 1201]:  # 鲜豆签到, 好友助力任务
                await self.receive_task(session, task_name, {"modelId": task['modelId'], "taskId": task['taskId'],
                                                             "taskType": task['taskType'], "plateCode": 3})
            elif task_type == 0:  # 浇水任务
                if 'todayFinishNum' in task:
                    times = 15 - task['todayFinishNum']
                else:
                    times = task['totalNum'] - task['finishNum']
                await self.watering(session, times=times, batch=False)  # 浇水10次
                await self.get_task_award(session, task)
            else:
                println('{}, 任务:《{}》暂未实现!'.format(self._account, task_name))

    async def get_water_info(self, session):
        """
        获取水滴信息
        :param session:
        :return:
        """
        res = await self.get(session, 'fruit/getWaterWheelInfo')
        if res['code'] != '0':
            return None
        return res['result']

    async def receive_water_wheel(self, session):
        """
        收取水车水滴
        :param session:
        :return:
        """
        water_info = await self.get_water_info(session)
        if not water_info:
            println('{}, 查询水滴信息失败!'.format(self._account))
            return
        if water_info['waterStorage'] < water_info['capacityLimit']:
            println('{}, 水车水滴未满, 暂不收取!'.format(self._account))
            return

        res = await self.get(session, 'fruit/collectWater')
        if res['code'] != '0':
            println('{}, 收取水车水滴失败!'.format(self._account))
        else:
            println('{}, 成功收取水车水滴!'.format(self._account))

    async def get_share_code(self):
        """
        获取助力码
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            dj_cookies = await self.login(session)
            if not dj_cookies:
                return
            println('{}, 登录成功...'.format(self._account))

        async with aiohttp.ClientSession(cookies=dj_cookies, headers=self.headers) as session:
            res = await self.get(session, 'task/list', {"modelId": "M10007", "plateCode": 4})
            if res['code'] != '0':
                println('{}, 无法获取助力码!'.format(self._account))
                return None
            code = None
            task_list = res['result']['taskInfoList']
            for task in task_list:
                if task['taskType'] == 1201:
                    body = {
                        'taskId': task['taskId'],
                        'uniqueId': task['uniqueId'],
                        'assistTargetPin': self._dj_pin,
                    }
                    code = json.dumps(body)
            if code:
                println('{}, 助力码:{}'.format(self._account, code))
            return code

    async def init(self, session):
        """
        初始化
        """
        res = await self.post(session, 'fruit/initFruit', {
            "cityId": str(self._city_id), "longitude": self._lng, "latitude": self._lat})
        if res['code'] != '0':
            println('{}, 初始化失败!'.format(self._account))
            return False
        return res['result']

    async def help_friend(self, session):
        """
        助力好友
        :return:
        """
        for code in DJ_FRUIT_CODE:
            try:
                params = json.loads(code)
            except Exception as e:
                println('{}, 助力失败, 助力码错误, {}'.format(self._account, e.args))
                continue
            if 'assistTargetPin' not in params:
                println('{}, 助力码错误, 无法助力!'.format(self._account))
                continue

            params.update({
                "plateCode": 5,
                "modelId": "M10007",
                "taskType": 1201,
            })
            user_pin = params['assistTargetPin']

            res = await self.get(session, 'task/finished', params)
            if res['code'] != '0':
                println('{}, 助力好友:{}失败!'.format(self._account, user_pin))
                break
            else:
                println('{}, 成功助力好友:{}!'.format(self._account, user_pin))
                await asyncio.sleep(1)

    async def set_notify_message(self, session):
        data = await self.init(session)
        if not data:
            return
        active_info = data['activityInfoResponse']
        message = '【活动名称】到家果园\n【活动账号】{}\n【活动昵称】{}\n'.format(self._pin, self._nickname)
        message += '【奖品名称】{}\n'.format(active_info['fruitName'])
        message += '【{}进度】{}/{}\n'.format(active_info['stageName'],
                                          active_info['curStageTotalProcess'] - active_info['curStageLeftProcess'],
                                          active_info['curStageTotalProcess'])
        if active_info['ifMaxProcess']:
            message += '【温馨提示】奖品可领取，请前往京东APP-京东到家-领免费水果领取, 并种植新一轮奖品!'

        message += '【剩余水滴】{}\n'.format(data['userResponse']['waterBalance'])

        self._message = message

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            dj_cookies = await self.login(session)
            if not dj_cookies:
                return
            println('{}, 登录成功...'.format(self._account))

        async with aiohttp.ClientSession(cookies=dj_cookies, headers=self.headers) as session:
            result = await self.init(session)
            if not result:
                return
            await self.help_friend(session)
            await self.do_task(session)  # 做任务
            await self.receive_water_red_packet(session)  # 领取浇水红包
            await self.receive_water_bottle(session)  # 领取水瓶
            await self.receive_water_wheel(session)  # 领取水车
            await self.watering(session, batch=True, keep_water=DJ_FRUIT_KEEP_WATER)
            await self.set_notify_message(session)


def start(pt_pin, pt_key):
    app = DjFruit(pt_pin, pt_key)
    asyncio.run(app.run())
    return app.message


if __name__ == '__main__':
    from utils.process import process_start

    process_start(start, '到家果园')
