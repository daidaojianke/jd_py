#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:25 下午
# @File    : jx_factory.py
# @Project : jd_scripts
# @Desc    : 京喜App->惊喜工厂
import moment
import time
import re
import json
import aiohttp
import asyncio
from furl import furl
from datetime import datetime
from urllib.parse import unquote, urlencode
from utils.algo import JxSignAlgoMixin
from utils.console import println


class JxFactory(JxSignAlgoMixin):
    """
    京喜工厂
    """
    headers = {
        'referer': 'https://st.jingxi.com/',
        'user-agent': 'jdpingou;android;4.11.0;11;a27b83d3d1dba1cc;network/wifi;model/RMX2121;appBuild/17304;partner'
                      '/oppo01;;session/136;aid/a27b83d3d1dba1cc;oaid/;pap/JA2019_3111789;brand/realme;eu'
                      '/1623732683334633;fv/4613462616133636;Mozilla/5.0 (Linux; Android 11; RMX2121 '
                      'Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
                      'Chrome/91.0.4472.120 Mobile Safari/537.36'
    }

    def __init__(self, pt_pin, pt_key):
        """
        """
        self._pt_pin = unquote(pt_pin)
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._host = 'https://m.jingxi.com/'
        self._factory_id = None  # 工厂ID
        self._nickname = None  # 用户昵称
        self._encrypt_pin = None
        self._inserted_electric = 0  # 已投入电量
        self._need_electric = 0  # 总共需要的电量
        self._production_id = 0  # 商品ID
        self._production_stage_progress = ''  # 生产进度
        self._phone_id = ''  # 设备ID
        self._pin = ''  # 账号ID
        self._random = None  #
        self._can_help = True  # 是否能帮好友打工
        self._active_id = ''

    async def request(self, session, path, params, method='GET'):
        """
        """
        try:
            time_ = datetime.now()
            default_params = {
                '_time': int(time_.timestamp() * 1000),
                'g_ty': 'ls',
                'callback': 'jsonp',
                'sceneval': '2',
                'g_login_type': '1',
                '_': int(time_.timestamp() * 1000) + 2,
                '_ste': '1',
                'timeStamp': int(time.time() * 1000),
            }
            params.update(default_params)
            url = self._host + path + '?' + urlencode(params)
            h5st = await self.encrypt(time_, url)
            params['h5st'] = h5st
            url = self._host + path + '?' + urlencode(params)
            if method == 'GET':
                response = await session.get(url=url)
            else:
                response = await session.post(url=url)
            text = await response.text()
            temp = re.search(r'\((.*)', text).group(1)
            data = json.loads(temp)
            if data['ret'] != 0:
                return data
            else:
                result = data['data']
                result['ret'] = 0
                return result
        except Exception as e:
            println('{}, 请求服务器数据失败:{}'.format(self._pt_pin, e.args))
            return {
                'ret': 50000,
                'msg': '请求服务器失败'
            }

    async def get_user_info_by_pin(self, session, pin):
        """
        根据pin获取用户信息
        :param session:
        :param pin:
        :return:
        """
        path = 'dreamfactory/userinfo/GetUserInfoByPin'
        params = {
            'zone': 'dream_factory',
            'pin': pin,
            'sharePin': '',
            'shareType': '',
            'materialTuanPin': '',
            'materialTuanId': '',
            'source': '',
            '_stk': '_time,materialTuanId,materialTuanPin,pin,sharePin,shareType,source,zone',
        }
        data = await self.request(session, path, params)
        if not data or data['ret'] != 0:
            return None
        return data

    async def get_user_info(self, session):
        """
        获取用户信息
        """
        path = 'dreamfactory/userinfo/GetUserInfo'
        params = {
            'pin': '',
            'sharePin': '',
            'shareType': '',
            'materialTuanPin': '',
            'materialTuanId': '',
            'source': '',
            'zone': 'dream_factory'
        }
        data = await self.request(session, path, params)
        if data['ret'] != 0:
            println('{}, 获取用户数据失败, {}!'.format(self._pt_pin, data['msg']))
            return None
        return data

    async def query_friend_list(self, session):
        """
        查询好友列表
        :param session:
        :return:
        """
        println('{}, 正在获取好友信息列表...'.format(self._pt_pin))
        res = []
        path = 'dreamfactory/friend/QueryFactoryManagerList'
        params = {
            'sort': 0,
            '_stk': '_time,sort,zone',
            'zone': 'dream_factory',
        }
        data = await self.request(session, path, params)
        if not data or data['ret'] != 0:
            println('{}, 获取好友列表失败!'.format(self._pt_pin))
            return []

        friend_list = data['list']

        for friend in friend_list:
            if 'encryptPin' not in friend:
                continue
            res.append(friend['encryptPin'])
        println('{}, 成功获取{}个好友信息!'.format(self._pt_pin, len(res)))
        return res

    async def collect_friend_electricity(self, session):
        """
        收取好友电量
        :param session:
        :return:
        """
        friend_pin_list = await self.query_friend_list(session)

        for friend_pin in friend_pin_list:
            friend_info = await self.get_user_info_by_pin(session, friend_pin)
            await asyncio.sleep(0.2)
            if not friend_info:
                continue
            if friend_info['ret'] != 0:
                continue
            if 'factoryList' not in friend_info or not friend_info['factoryList']:
                continue

            if 'user' not in friend_info or not friend_info['user']:
                continue

            factory_id = friend_info['factoryList'][0]['factoryId']
            pin = friend_info['user']['pin']
            nickname = friend_info['user']['nickname']
            await self.query_user_electricity(session, factory_id=factory_id, pin=pin, nickname=nickname)
            await asyncio.sleep(1)

    async def collect_user_electricity(self, session, phone_id=None, factory_id=None,
                                       nickname=None, pin=None, double_flag=1):
        """
        收取发电机电量, 默认收取自己的
        :param pin:
        :param nickname:
        :param double_flag: 是否翻倍
        :param factory_id: 工厂ID
        :param phone_id: 手机设备ID
        :param session:
        :return:
        """
        path = 'dreamfactory/generator/CollectCurrentElectricity'

        if not phone_id:
            phone_id = self._phone_id
        if not factory_id:
            factory_id = self._factory_id
        if not nickname:
            nickname = self._nickname
        params = {
            'pgtimestamp': str(int(time.time() * 1000)),
            'apptoken': '',
            'phoneID': phone_id,
            'factoryid': factory_id,
            'doubleflag': double_flag,
            'timeStamp': 'undefined',
            '_stk': '_time,apptoken,doubleflag,factoryid,pgtimestamp,phoneID,zone',
            'zone': 'dream_factory',
        }
        if pin:
            params['master'] = pin
            params['_stk'] = '_time,apptoken,doubleflag,factoryid,master,pgtimestamp,phoneID,zone'
        data = await self.request(session, path, params, 'GET')
        if not data or data['ret'] != 0:
            println('{}, 收取用户:{}的电量失败, {}'.format(self._pt_pin, nickname, data))
        else:
            println('{}, 成功收取用户:{}的电量:{}!'.format(self._pt_pin, nickname, data['CollectElectricity']))

    async def query_user_electricity(self, session, factory_id=None, phone_id=None, nickname=None, pin=None):
        """
        查询当前用户发电机电量, 如果满了就收取电量
        """
        if not factory_id:
            factory_id = self._factory_id
        if not phone_id:
            phone_id = self._phone_id
        if not nickname:
            nickname = self._nickname

        path = 'dreamfactory/generator/QueryCurrentElectricityQuantity'
        body = {
            'factoryid': factory_id,
            '_stk': '_time,factoryid,zone',
            'zone': 'dream_factory'
        }
        if pin:
            body['master'] = pin
            body['_stk'] = '_time,factoryid,master,zone'
        data = await self.request(session, path, body)
        if data['ret'] != 0:
            println('{}, 查询电量失败！'.format(self._pt_pin))
            return

        if int(data['currentElectricityQuantity']) >= data['maxElectricityQuantity']:
            await self.collect_user_electricity(session, phone_id, factory_id, nickname, pin)
        else:
            println('{}, 用户:{}, 当前电量:{}/{}, 不收取!'.format(self._pt_pin,
                                                         nickname, int(data['currentElectricityQuantity']),
                                                         data['maxElectricityQuantity']))

    async def get_active_id(self, session):
        """
        获取每期拼团的活动ID
        :param session:
        :return:
        """
        try:
            println('{}, 正在获取拼团活动ID...'.format(self._pt_pin))
            url = 'https://wqsd.jd.com/pingou/dream_factory/index.html'
            response = await session.get(url)
            text = await response.text()
            res = re.search(r'window\._CONFIG = (.*) ;var __getImgUrl', text).group(1)
            data = json.loads(res)
            for item in data:
                if 'skinConfig' not in item:
                    continue
                conf_list = item['skinConfig']
                for conf in conf_list:
                    if 'adConfig' not in conf:
                        continue
                    ad_list = conf['adConfig']
                    for ad in ad_list:
                        if not ad['start'] or not ad['end']:
                            continue
                        start_date = moment.date(ad['start'])
                        end_date = moment.date(ad['end'])
                        now = moment.now()
                        if start_date < now < end_date:
                            url = furl(ad['link'].split(',')[0])
                            active_id = url.args.get('activeId', '')
                            println('{}, 拼团活动ID为:{}'.format(self._pt_pin, active_id))
                            return active_id
        except Exception as e:
            println('{}, 获取拼团活动ID失败, {}!'.format(self._pt_pin, e.args))
            return ''

    async def init(self, session):
        """
        初始化
        """
        user_info = await self.get_user_info(session)
        if not user_info:
            return False
        if 'factoryList' not in user_info or not user_info['factoryList']:
            println('{}, 未开启活动!'.format(self._pt_pin))
            return False

        self._factory_id = user_info['factoryList'][0]['factoryId']

        if 'productionList' not in user_info or not user_info['productionList']:
            println('{}, 未选择商品!'.format(self._pt_pin))
        else:
            self._inserted_electric = user_info['productionList'][0]['investedElectric']
            self._need_electric = user_info['productionList'][0]['needElectric']
            self._production_id = user_info['productionList'][0]['productionId']

        if 'user' not in user_info:
            println('{}, 没有找到用户信息!'.format(self._pt_pin))
            return False
        self._pin = user_info['user']['pin']
        self._phone_id = user_info['user']['deviceId']
        self._encrypt_pin = user_info['user']['encryptPin']
        self._nickname = user_info['user']['nickname']
        return True

    async def query_work_info(self, session):
        """
        查询招工/打工情况
        :param session:
        :return:
        """
        path = 'dreamfactory/friend/QueryFriendList'
        params = {
            'body': '',
            '_stk': '_time,zone',
            'zone': 'dream_factory',
        }
        data = await self.request(session, path, params)
        if not data:
            return
        println('{}, 今日帮好友打工:{}/{}次!'.format(self._pt_pin, len(data['assistListToday']), data['assistNumMax']))

        # 打工次数满了，无法打工
        if len(data['assistListToday']) >= data['assistNumMax']:
            self._can_help = False

        println('{}, 今日招工:{}/{}次!'.format(self._pt_pin, len(data['hireListToday']), data['hireNumMax']))

    async def get_task_award(self, session, task):
        """
        领取任务奖励
        :param task:
        :param session:
        :return:
        """
        path = 'newtasksys/newtasksys_front/Award'
        params = {
            'bizCode': 'dream_factory',
            'source': 'dream_factory',
            'taskId': task['taskId'],
            '_stk': '_time,bizCode,source,taskId'
        }
        data = await self.request(session, path, params)

        if not data or data['ret'] != 0:
            println('{}, 领取任务:《{}》奖励失败, {}'.format(self._pt_pin, task['taskName'], data['msg']))
            return
        num = data['prizeInfo'].replace('\n', '')
        println('{}, 领取任务:《{}》奖励成功, 获得电力:{}!'.format(self._pt_pin, task['taskName'], num))

    async def do_task_list(self, session):
        """
        获取任务列表
        :param session:
        :return:
        """
        path = 'newtasksys/newtasksys_front/GetUserTaskStatusList'
        params = {
            'bizCode': 'dream_factory',
            'source': 'dream_factory',
            '_stk': '_time,bizCode,source'
        }
        data = await self.request(session, path, params)
        if not data or data['ret'] != 0:
            println('{}, 获取任务列表失败!'.format(self._pt_pin))
            return
        task_list = data['userTaskStatusList']

        for task in task_list:
            # 任务完成并且没有领取过奖励去领取奖励
            if task['completedTimes'] >= task['targetTimes'] and task['awardStatus'] != 1:
                await self.get_task_award(session, task)
                await asyncio.sleep(1)
                continue

            if task['taskType'] in [2, 9]:
                await self.do_task(session, task)
                await asyncio.sleep(1)

    async def do_task(self, session, task):
        """
        做任务
        :param task:
        :param session:
        :return:
        """
        if task['completedTimes'] >= task['targetTimes']:
            println('{}, 任务《{}》今日已完成!'.format(self._pt_pin, task['taskName']))
            return

        path = 'newtasksys/newtasksys_front/DoTask'
        params = {
            'source': 'dreamfactory',
            'bizCode': 'dream_factory',
            '_stk': '_time,bizCode,configExtra,source,taskId',
            'taskId': task['taskId'],
            'configExtra': ''
        }
        for i in range(task['completedTimes'], task['targetTimes']):
            data = await self.request(session, path, params)
            if not data or data['ret'] != 0:
                break
            await asyncio.sleep(1)
            await self.get_task_award(session, task)

    async def query_tuan_info(self, session, active_id=None):
        """
        查询开团信息
        :return:
        """
        if not active_id:
            active_id = self._active_id
        path = 'dreamfactory/tuan/QueryActiveConfig'
        params = {
            'activeId': active_id,
            'tuanId': '',
            '_stk': '_time,activeId,tuanId',
        }
        data = await self.request(session, path, params)
        if not data or data['ret'] != 0:
            println('{}, 获取团ID失败!'.format(self._pt_pin))
            return []
        return data['userTuanInfo']

    async def create_tuan(self, session):
        """
        :return:
        """
        self._active_id = await self.get_active_id(session)
        tuan_info = await self.query_tuan_info(session)

        if tuan_info['isOpenTuan'] != 2:
            path = 'dreamfactory/tuan/CreateTuan'
            params = {
                'activeId': self._active_id,
                'isOpenApp': 1,
                '_stk': '_time,activeId,isOpenApp'
            }
            data = await self.request(session, path, params)
            if not data or data['ret'] != 0:
                println('{}, 开团失败!'.format(self._pt_pin))
                return ''
            println('{}, 开团成功, 团ID：{}!'.format(self._pt_pin, data['tuanId']))
            return data['tuanId']

        println('{}, 已开过团, 团ID: {}!'.format(self._pt_pin, tuan_info['tuanId']))
        return tuan_info['tuanId']

    async def join_tuan(self, session, tuan_id=None):
        """
        参团
        :param tuan_id:
        :param session:
        :return:
        """
        path = 'dreamfactory/tuan/JoinTuan'
        params = {
            'activeId': self._active_id,
            'tuanId': 'FfCW8rRQrxfpaQfG_COFDw==',
            '_stk': '_time,activeId,tuanId'
        }
        data = await self.request(session, path, params)

        if not data:
            println('{}, 无法参团, 团ID:{}!'.format(self._pt_pin, tuan_id))
            return

        if data['ret'] in [10208, 0]:
            println('{}, 已成功参团, 团ID: {}'.format(self._pt_pin, tuan_id))
        else:
            println('{}, 无法参团, 团ID:{}, {}'.format(self._pt_pin, tuan_id, data['msg']))

    async def run(self):
        """
        程序入口
        """
        await self.get_encrypt()
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            success = await self.init(session)
            if not success:
                println('{}, 初始化失败!'.format(self._pt_pin))
                return
            await self.create_tuan(session)
            await self.join_tuan(session)
            # await self.do_task_list(session)  # 做任务
            # await self.query_user_electricity(session)  # 查询当前用户电量, 满了则收取电量
            # await self.collect_friend_electricity(session)


def start(pt_pin, pt_key):
    """
    程序入口
    """
    app = JxFactory(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    from config import JD_COOKIES

    start(*JD_COOKIES[0].values())
