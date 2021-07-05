#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/5 9:52 上午
# @File    : jr_money_tree.py
# @Project : jd_scripts
# @Desc    : 金果摇钱树
import aiohttp
import random
import time
import asyncio
import json

from urllib.parse import unquote, urlencode, quote
from furl import furl
from config import USER_AGENT, JD_MONEY_TREE_SHARE_PIN

from utils.console import println
from utils.notify import notify
from utils.process import process_start


class JdMoneyTree:
    """
    金果摇钱树
    """
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'Origin': 'https://uua.jr.jd.com',
        'Referer': 'https://uua.jr.jd.com/',
        'User-Agent': USER_AGENT,
    }
    """
    金果摇钱树
    """

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._pt_pin = unquote(pt_pin)
        self._host = 'https://ms.jr.jd.com/gw/generic/uc/h5/m/'
        self._nickname = None
        self._tree_name = None
        self._tree_level = None
        self._share_pin = None
        self._user_id = None
        self._user_token = None
        self._fruit = 0  # 金果数量
        self._jt_rest = None

    async def request(self, session, path, params, method='post'):
        """
        :param method:
        :param params:
        :param session:
        :param path:
        :return:
        """
        try:
            session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
            url = self._host + path + '?_={}'.format(int(time.time() * 1000))
            if method == 'post':
                body = 'reqData={}'.format(quote(json.dumps(params)))
                response = await session.post(url=url, data=body)
            else:
                response = await session.get(url, body=params)

            text = await response.text()

            data = json.loads(text)

            await asyncio.sleep(0.5)

            if data['resultCode'] == 0:
                return data['resultData']
            else:
                return None
        except Exception as e:
            println('{}, 请求服务器数据失败, {}'.format(self._pt_pin, e.args))

    async def post(self, session, path, params):
        """
        POST请求
        :param session:
        :param path:
        :param params:
        :return:
        """
        return await self.request(session, path, params, 'post')

    async def get(self, session, path, params):
        """
        GET请求
        :param session:
        :param path:
        :param params:
        :return:
        """
        return await self.request(session, path, params, 'get')

    async def login(self, session):
        """
        获取用户信息
        :param session:
        :return:
        """
        params = {
            "sharePin": "",
            "shareType": 1,
            "channelLV": "",
            "source": 0,
            "riskDeviceParam": "{}"
        }
        data = await self.post(session, 'login', params)

        if not data or data['code'] != '200':
            println('{}, 无法获取用户数据!'.format(self._pt_pin))
            return False

        data = data['data']

        if not data['realName']:
            println('{}运行失败, 此账号未实名认证或者未参与过此活动: \n  ①如未参与活动,请先去京东app参加摇钱树活动入口：我的->游戏与互动->查看更多\n  '
                    '②如未实名认证,请进行实名认证!'.format(self._pt_pin))

        self._nickname = data['nick']
        self._tree_name = data['treeInfo']['treeName']
        self._tree_level = data['treeInfo']['level']
        self._share_pin = data['sharePin']
        self._user_id = data['userInfo']
        self._user_token = data['userToken']
        self._fruit = data['treeInfo']['fruit']
        self._jt_rest = data['jtRest']

        return True

    async def daily_sign(self, session):
        """
        每日签到
        :param session:
        :return:
        """
        index_params = {"source": 0, "riskDeviceParam": "{}"}
        index_data = await self.request(session, 'signIndex', index_params)
        if not index_data or index_data['code'] != '200':
            println('{}, 无法获取签到数据!'.format(self._pt_pin))
            return
        index_data = index_data['data']
        if index_data['canSign'] != 2:
            println('{}, 今日已签到!'.format(self._pt_pin))
            return

        sign_params = {"source": 0, "signDay": index_data['signDay'], "riskDeviceParam": "{}"}
        data = await self.post(session, 'signOne', sign_params)
        if data['code'] == '200' and data['data']['result']:
            println('{}, 签到成功!'.format(self._pt_pin))

            if index_data['signDay'] == 7:  # 领取7日签到奖品
                params = {
                    "source": 2,
                    "awardType": 2,
                    "deviceRiskParam": 1,
                    "riskDeviceParam": "{}",
                }
                res = await self.request(session, 'getSignAward', params)
                println('{}, 领取7日签到奖励结果:{}'.format(self._pt_pin, res))

        else:
            println('{}, 签到失败!'.format(self._pt_pin))

    async def do_browser_work(self, session, work):
        """
        浏览任务
        :param session:
        :param work:
        :return:
        """
        if work['workStatus'] == 2:
            println('{}, 浏览任务《{}》今日已完成!'.format(self._pt_pin, work['workName']))
            return

        url = furl(work['url'])
        read_time = int(url.args.get('readTime'))

        # 执行任务
        println('{}, 开始执行任务《{}》, 需要等待{}秒!'.format(self._pt_pin, work['workName'], read_time))
        url = 'https://ms.jr.jd.com/gw/generic/mission/h5/m/' \
              'queryMissionReceiveAfterStatus?reqData={}'.format(quote(json.dumps({'missionId': str(work['mid'])})))
        await session.post(url=url)
        await asyncio.sleep(read_time)

        # 提交任务
        url = 'https://ms.jr.jd.com/gw/generic/mission/h5/m/finishReadMission?' \
              'reqData={}'.format(quote(json.dumps({'missionId': str(work['mid']), 'readTime': read_time})))
        await session.post(url=url)

        # 完成任务
        await self.post(session, 'doWork', {"source": 0, "workType": 6, "opType": 4,
                                            "mid": work['mid'], "riskDeviceParam": "{}"})

        # 领取奖励
        res = await self.post(session, 'doWork', {"source": 0, "workType": 6, "opType": 2,
                                                  "mid": str(work['mid']), "riskDeviceParam": "{}"})
        if res['data']['opResult'] == 0:
            println('{}, 领取任务《{}》奖励结果成功, 获得{}金果!'.format(self._pt_pin, work['workName'], res['data']['prizeAmount']))
        else:
            println('{}, 领取任务《{}》奖励结果失败, {}'.format(self._pt_pin, work['workName'], res['data']['opMsg']))

    async def daily_work(self, session):
        """
        每日任务
        :param session:
        :return:
        """
        params = {"source": 0, "linkMissionIds": [], "LinkMissionIdValues": [], "riskDeviceParam": ""}
        work_data = await self.post(session, 'dayWork', params)
        if not work_data or work_data['code'] != '200':
            println('{}, 无法获取任务列表!'.format(self._pt_pin))
            return

        work_list = work_data['data']  # 任务列表

        for work in work_list:
            if work['workType'] == 1:  # 三餐签到
                if work['workStatus'] in [-1, 2]:
                    println('{}, 三餐签到不在时间范围内或已完成过!'.format(self._pt_pin))
                    continue
                res = await self.request(session, 'doWork', {"source": 2, "workType": work['workType'], "opType": 2})
                println('{}, 三餐签到结果:{}!'.format(self._pt_pin, res))
            if work['workType'] == 2:  # 分享任务
                if work['workStatus'] == 2:
                    println('{}, 分享任务今日已完成!'.format(self._pt_pin))
                    continue
                else:
                    share_res = await self.request(session, 'doWork', {"source": 0, "workType": 2, "opType": 1})
                    println('{}, 进行分享任务结果:{}'.format(self._pt_pin, share_res))

                    award_res = await self.request(session, 'doWork', {"source": 0, "workType": 2, "opType": 2})
                    println('{}, 领取分享任务奖励:{}'.format(self._pt_pin, award_res))

            if work['workType'] == 6 and 'readTime' in work['url']:  # 浏览任务
                await self.do_browser_work(session, work)

    async def harvest(self, session):
        """
        收金果
        :param session:
        :return:
        """
        params = {
            "source": 0,
            "sharePin": self._share_pin,
            "userId": self._user_id,
            "userToken": self._user_token,
            "shareType": "1",
            "channel": "",
            "riskDeviceParam": "{}"
        }
        data = await self.post(session, 'harvest', params)
        if data['code'] != '200':
            println('{}, 收金果异常:{}'.format(self._pt_pin, data))
            return
        data = data['data']
        println('{}, 收金果成功, 获得金果:{}个!'.format(self._pt_pin, data['fruitNumInLimitedTimeTask']))

    async def sell(self, session):
        """
        卖金果
        :return:
        """
        await self.login(session)  # 刷新金果数量
        params = {
            "source": 2,
            "jtCount": 7.000000000000001,
            "riskDeviceParam": "{}",
        }
        if self._fruit >= 8000 * 7:
            if self._jt_rest == 0:
                println('{}, 今日已卖出5.6万金果(已达上限)，获得0.07金贴!'.format(self._pt_pin))
                return
            res = await self.request(session, 'sell', params)
            println('{}, 卖出金果结果:{}'.format(self._pt_pin, res))
        else:
            println('{}, 当前金果数量不够兑换 0.07金贴!'.format(self._pt_pin))

    async def work_for_friend(self, session):
        """
        帮好友打工
        :param session:
        :return:
        """
        share_pin_list = []
        for share_pin in JD_MONEY_TREE_SHARE_PIN:
            if share_pin == self._share_pin:
                continue
            share_pin_list.append(share_pin)

        # 随机帮一名好友打工
        share_pin = random.choice(share_pin_list)
        params = {
            "sharePin": share_pin,
            "shareType": "1",
            "channelLV": "",
            "source": 0,
            "riskDeviceParam": "{}"
        }
        data = await self.request(session, 'login', params)
        if data['code'] == '200':
            println('{}, 正在帮好友打工!'.format(self._pt_pin))
        else:
            println('{}, 无法为好友打工!'.format(self._pt_pin))

    async def steal_fruit(self, session):
        """
        偷金果
        :param session:
        :return:
        """
        params = {"source": 0, "riskDeviceParam": "{}"}
        friend_data = await self.request(session, 'friendRank', params)
        if friend_data['code'] != '200':
            println('{}, 获取好友列表失败!'.format(self._pt_pin))
            return
        friend_list = friend_data['data']
        count = 0
        total = 0
        for friend in friend_list:
            if not friend['steal']:  # 跳过不可以偷的
                continue

            params = {
                "source": 0,
                "friendPin": friend['encryPin'],
                "riskDeviceParam": "{}"
            }

            # 找到好友的摇钱树
            tree_data = await self.request(session, 'friendTree', params)
            if tree_data['code'] != '200':
                println('{}, 无法获取好友摇钱树信息!'.format(self._pt_pin))
                continue
            store_id = tree_data['data']['stoleInfo']

            params = {
                "source": 0,
                "friendPin": friend['encryPin'],
                "stoleId": store_id,
                "riskDeviceParam": "{}"
            }
            res = await self.request(session, 'stealFruit', params)
            if res['code'] == '200':
                println('{}, 成功偷取好友{}个金果!'.format(self._pt_pin, res['data']['amount']))
                count += 1
                total += res['data']['amount']
            else:
                println('{}, 偷取好友金果失败!'.format(self._pt_pin))

        println('{}, 共偷取{}个好友金果, 总共获得{}个金果!'.format(self._pt_pin, count, total))

    async def notify_result(self, session):
        """
        查询摇钱树及金果金贴信息并发送通知
        :param session:
        :return:
        """
        await self.login(session)

        params = {"source": 0, "riskDeviceParam": "{}"}
        data = await self.request(session, 'myWealth', params)
        message = '【活动名称】摇钱树\n【京东账号】{}\n【摇钱树等级】{}\n【金果数量】{}\n【金贴数量】{}' \
                  ''.format(self._pt_pin, self._tree_level, data['data']['gaAmount'], data['data']['gcAmount'] / 100)

        println('\n')
        println(message)
        notify(message)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            is_success = await self.login(session)
            if not is_success:
                println('{}, 登录失败, 退出程序...'.format(self._pt_pin))
            await self.daily_sign(session)  # 每日签到
            await self.daily_work(session)  # 每日任务
            await self.harvest(session)  # 收金果
            await self.sell(session)  # 卖金果
            await self.work_for_friend(session)  # 帮好友打工
            await self.steal_fruit(session)  # 偷好友金果
            await self.notify_result(session)


def start(pt_pin, pt_key):
    """
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdMoneyTree(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    process_start(start, '金果摇钱树')
