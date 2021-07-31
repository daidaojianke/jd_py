#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:27 下午
# @File    : jd_farm.py
# @Project : jd_scripts
# @Cron    : 15 6-18/6 * * *
# @Desc    : 京东APP-东东农场

import asyncio
import math
import time
from datetime import datetime

import aiohttp
import json

from urllib.parse import unquote, quote
from utils.console import println
from config import USER_AGENT, JD_FARM_CODE, JD_FARM_BEAN_CARD, JD_FARM_RETAIN_WATER


class JdFarm:
    """
    京东农场
    """
    headers = {
        'user-agent': USER_AGENT,
        # 'content-type': 'application/json',
        'x-requested-with': 'com.jingdong.app.mall',
        'sec-fetch-mode': 'cors',
        'origin': 'https://carry.m.jd.com',
        'sec-fetch-site': 'same-site',
        'referer': 'https://carry.m.jd.com/babelDiy/Zeus/3KSjXqQabiTuD1cJ28QskrpWoBKT/index.html'
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._pt_pin = unquote(pt_pin)
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._farm_info = None
        self._message = None  # 消息通知

    @property
    def message(self):
        return self._message

    async def request(self, session, function_id, body=None):
        """
        :param session:
        :param body:
        :param function_id:
        :return:
        """
        try:
            if not body:
                body = dict()
            if 'version' not in body:
                body['version'] = 13
            if 'channel' not in body:
                body['channel'] = 1

            url = 'https://api.m.jd.com/client.action?functionId={}&body={}&appid=wh5'.format(function_id,
                                                                                              quote(json.dumps(body)))
            response = await session.get(url=url)
            data = await response.json()
            await asyncio.sleep(1)
            return data
        except Exception as e:
            println('{}, 获取服务器数据错误:{}'.format(self._pt_pin, e.args))

    async def init_for_farm(self, session):
        """
        初始化农场数据
        :param session:
        :return:
        """
        data = await self.request(session, 'initForFarm')
        if data['code'] != '0' or 'farmUserPro' not in data:
            return None
        return data['farmUserPro']

    async def sign(self, session):
        """
        :param session:
        :return:
        """
        data = await self.request(session, 'signForFarm')
        if data['code'] == '0':
            println('{}, 签到成功, 已连续签到{}天!'.format(self._pt_pin, data['signDay']))
        elif data['code'] == '7':
            println('{}, 今日已签到过!'.format(self._pt_pin))
        else:
            println('{}, 签到失败, {}'.format(self._pt_pin, data['message']))

        if 'todayGotWaterGoalTask' in data and data['todayGotWaterGoalTask']['canPop']:
            await asyncio.sleep(1)
            data = await self.request(session, 'gotWaterGoalTaskForFarm', {'type': 3})
            if data['code'] == '0':
                println('{}, 被水滴砸中, 获得{}g水滴!'.format(self._pt_pin, data['addEnergy']))

    async def do_browser_tasks(self, session, tasks):
        """
        做浏览任务
        :param tasks:
        :param session:
        :return:
        """
        for task in tasks:
            task_name = task['mainTitle']
            println('{}, 正在进行浏览任务: 《{}》...'.format(self._pt_pin, task_name))
            task_res = await self.request(session, 'browseAdTaskForFarm', {'advertId': task['advertId'], 'type': 0})
            # 完成任务去领取奖励
            if task_res['code'] == '0' or task_res['code'] == '7':
                task_award = await self.request(session, 'browseAdTaskForFarm',
                                                {'advertId': str(task['advertId']), 'type': 1})
                if task_award['code'] == '0':
                    println('{}, 成功领取任务:《{}》的奖励, 获得{}g水滴！'.format(self._pt_pin, task_name, task_award['amount']))
                else:
                    println('{}, 领取任务:《{}》的奖励失败, {}'.format(self._pt_pin, task_name, task_award))
            else:
                println('{}, 浏览任务:《{}》, 结果:{}'.format(self._pt_pin, task_name, task_res))

    async def get_encrypted_pin(self, session):
        """
        获取加密pin参数
        :return:
        """
        try:
            response = await session.get(
                'https://api.m.jd.com/client.action?functionId=getEncryptedPinColor&body=%7B%22version%22%3A14%2C'
                '%22channel%22%3A1%2C%22babelChannel%22%3A0%7D&appid=wh5')
            text = await response.text()
            data = json.loads(text)
            return data['result']
        except Exception as e:
            println('{}, 获取pin参数出错, {}'.format(self._pt_pin, e.args))

    async def get_award_of_invite_friend(self, session):
        """
        获取邀请好友奖励
        :param session:
        :return:
        """
        data = await self.request(session, 'friendListInitForFarm')
        if data['code'] != '0':
            println('{}, 获取好友列表失败...'.format(self._pt_pin))
            return
        invite_friend_count = data['inviteFriendCount']  # 今日邀请好友个数
        invite_friend_max = data['inviteFriendMax']  # 每日邀请上限
        println('{}, 今日已邀请好友{}个 / 每日邀请上限{}个'.format(self._pt_pin, invite_friend_count, invite_friend_max))
        friends = data['friends']  # 好友列表
        cur_friend_count = len(friends)  # 当前好友数量

        if cur_friend_count > 0:
            println('{}, 开始删除{}个好友, 可拿每天的邀请奖励!'.format(self._pt_pin, cur_friend_count))
            for friend in friends:
                res = await self.request(session, 'deleteFriendForFarm', {
                    'shareCode': friend['shareCode']
                })
                if res['code'] == '0':
                    println('{}, 成功删除好友:{}'.format(self._pt_pin, friend['nickName']))

        m_pin = await self.get_encrypted_pin(session)

        for code in JD_FARM_CODE:
            # 自己不能邀请自己成为好友
            if code == self._farm_info['shareCode']:
                continue
            res = await self.request(session, 'initForFarm', {
                'shareCode': code + '-inviteFriend',
                "mpin": m_pin,
                'version': 13,
                "babelChannel": 0,
                'channel': 1
            })
            if res['helpResult']['code'] == '0' or res['helpResult']['code'] == '20':
                println('{}, 接受邀请成功, 已成为{}的好友!'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName']))
            else:
                println('{}, 接受好友邀请失败, {}'.format(self._pt_pin, res['helpResult']))

        data = await self.request(session, 'friendListInitForFarm')
        if data['inviteFriendCount'] > 0:
            if data['inviteFriendCount'] > data['inviteFriendGotAwardCount']:
                res = await self.request(session, 'awardInviteFriendForFarm')
                println('{}, 领取邀请好友奖励结果:{}'.format(self._pt_pin, res))
        else:
            println('{}, 今日未邀请过好友!'.format(self._pt_pin))

    async def timed_collar_drop(self, session):
        """
        定时领水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'gotThreeMealForFarm')
        if data['code'] == '0':
            println('{}, 【定时领水滴】获得 {}g!'.format(self._pt_pin, data['amount']))
        else:
            println('{}, 【定时领水滴】失败,{}!'.format(self._pt_pin, data))

    async def do_friend_water(self, session):
        """
        给好友浇水
        :param session:
        :return:
        """
        data = await self.request(session, 'friendListInitForFarm')
        if 'friends' not in data:
            println('{}, 获取好友列表失败!'.format(self._pt_pin))
            return
        friends = data['friends']
        if len(friends) == 0:
            println('{}, 暂无好友!'.format(self._pt_pin))
            return

        count = 0
        for friend in friends:
            if friend['friendState'] != 1:
                continue
            count += 1
            res = await self.request(session, 'waterFriendForFarm', {'shareCode': friend['shareCode']})
            println('{}, 为第{}个好友({})浇水, 结果：{}'.format(self._pt_pin, count, friend['nickName'], count, res))
            if res['code'] == '11':
                println('{}, 水滴不够, 退出浇水!'.format(self._pt_pin))
                return

    async def clock_in(self, session):
        """
        打卡领水
        :param session:
        :return:
        """
        println('{}, 开始打卡领水活动(签到, 关注)'.format(self._pt_pin))
        res = await self.request(session, 'clockInInitForFarm')
        if res['code'] == '0':
            if not res['todaySigned']:
                println('{}, 开始今日签到!'.format(self._pt_pin))
                data = await self.request(session, 'clockInForFarm', {'type': 1})
                println('{}, 打卡结果{}'.format(self._pt_pin, data))
                if data['signDay'] == 7:
                    println('{}, 开始领取--惊喜礼包!'.format(self._pt_pin))
                    gift_data = await self.request(session, 'clockInForFarm', {"type": 2})
                    println('{}, 惊喜礼包获得{}g水滴!'.format(self._pt_pin, gift_data['amount']))

        if res['todaySigned'] and res['totalSigned'] == 7:  # 签到七天领惊喜礼包
            println('{}, 开始领取--惊喜礼包!'.format(self._pt_pin))
            gift_data = await self.request(session, 'clockInForFarm', {"type": 2})
            if gift_data['code'] == '7':
                println('{}, 领取惊喜礼包失败, 已领取过!'.format(self._pt_pin))
            elif gift_data['code'] == '0':
                println('{}, 惊喜礼包获得{}g水滴!'.format(self._pt_pin, gift_data['amount']))
            else:
                println('{}, 领取惊喜礼包失败, 原因未知!'.format(self._pt_pin))

        if res['themes'] and len(res['themes']) > 0:  # 限时关注得水滴
            for item in res['themes']:
                if not item['hadGot']:
                    println('{}, 关注ID：{}'.format(self._pt_pin, item['id']))
                    data1 = await self.request(session, 'clockInFollowForFarm', {
                        'id': str(item['id']),
                        'type': 'theme',
                        'step': 1
                    })
                    if data1['code'] == '0':
                        data2 = await self.request(session, 'clockInFollowForFarm', {
                            'id': item['id'],
                            'type': 'theme',
                            'step': 2
                        })
                        if data2['code'] == '0':
                            println('{}, 关注{}, 获得水滴{}g'.format(self._pt_pin, item['id'], data2['amount']))
        println('{}, 结束打卡领水活动(签到, 关注)'.format(self._pt_pin))

    async def water_drop_rain(self, session, task):
        """
        :param task:
        :param session:
        :return:
        """
        if task['f']:
            println('{}, 两次水滴雨任务已全部完成!'.format(self._pt_pin))
            return

        if task['lastTime'] and int(time.time() * 1000) < task['lastTime'] + 3 * 60 * 60 * 1000:
            println('{}, 第{}次水滴雨未到时间:{}!'.format(self._pt_pin, task['winTimes'] + 1,
                                                 datetime.fromtimestamp(int((task['lastTime']
                                                                             + 3 * 60 * 60 * 1000) / 1000))))
            return

        for i in range(task['config']['maxLimit']):
            data = await self.request(session, 'waterRainForFarm')
            if data['code'] == '0':
                println('{}, 第{}次水滴雨获得水滴:{}g'.format(self._pt_pin, task['winTimes'] + 1, data['addEnergy']))
            else:
                println('{}, 第{}次水滴雨执行错误:{}'.format(self._pt_pin, task['winTimes'] + 1, data))

    async def get_extra_award(self, session):
        """
        领取额外奖励
        :return:
        """
        data = await self.request(session, 'masterHelpTaskInitForFarm')

        if 'masterHelpPeoples' not in data or len(data['masterHelpPeoples']) < 5:
            println('{}, 获取助力信息失败或者助力不满5人, 无法领取额外奖励!'.format(self._pt_pin))
            return

        award_res = await self.request(session, 'masterGotFinishedTaskForFarm')
        if award_res['code'] == '0':
            println('{}, 成功领取好友助力奖励, {}g水滴!'.format(self._pt_pin, award_res['amount']))
        else:
            println('{}, 领取好友助力奖励失败, {}'.format(self._pt_pin, award_res))

    async def turntable(self, session):
        """
        天天抽奖
        :return:
        """
        data = await self.request(session, 'initForTurntableFarm')
        if data['code'] != '0':
            println('{}, 当前无法参与天天抽奖!'.format(self._pt_pin))
            return

        if not data['timingGotStatus']:
            if data['sysTime'] > (data['timingLastSysTime'] + 60 * 60 * data['timingIntervalHours'] * 1000):
                res = await self.request(session, 'timingAwardForTurntableFarm')
                println('{}, 领取定时奖励结果:{}'.format(self._pt_pin, res))
            else:
                println('{}, 免费赠送的抽奖机会未到时间!'.format(self._pt_pin))
        else:
            println('{}, 4小时候免费赠送的抽奖机会已领取!'.format(self._pt_pin))

        if 'turntableBrowserAds' in data and len(data['turntableBrowserAds']) > 0:
            count = 1
            for item in data['turntableBrowserAds']:
                if item['status']:
                    println('{}, 天天抽奖任务:{}, 今日已完成过!'.format(self._pt_pin, item['main']))
                    continue
                res = await self.request(session, 'browserForTurntableFarm', {'type': 1, 'adId': item['adId']})
                println('{}, 完成天天抽奖任务:《{}》, 结果:{}'.format(self._pt_pin, item['main'], res))
                await asyncio.sleep(1)
                award_res = await self.request(session, 'browserForTurntableFarm', {'type': 2, 'adId': item['adId']})
                println('{}, 领取天天抽奖任务:《{}》奖励, 结果:{}'.format(self._pt_pin, item['main'], award_res))
                count += 1

        println('{}, 开始天天抽奖--好友助力--每人每天只有三次助力机会!'.format(self._pt_pin))
        for code in JD_FARM_CODE:
            if code == self._farm_info['shareCode']:
                continue
            res = await self.request(session, 'initForFarm', {
                "imageUrl": "",
                "nickName": "",
                "shareCode": code + '-3',
                "babelChannel": "3"
            })
            if res['helpResult']['code'] == '0':
                println('{}, 天天抽奖-成功助力用户:《{}》 !'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName']))
            elif res['helpResult']['code'] == '11':
                println('{}, 天天抽奖-无法重复助力用户:《{}》!'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName']))
            elif res['helpResult']['code'] == '13':
                println('{}, 天天抽奖-助力用户:《{}》失败, 助力次数已用完!'.format(self._pt_pin,
                                                                res['helpResult']['masterUserInfo']['nickName']))
            else:
                println('{}, 天天抽奖助力用户:《{}》失败, 原因未知!'.format(self._pt_pin,
                                                            res['helpResult']['masterUserInfo']['nickName']))
        println('{}, 完成天天抽奖--好友助力!'.format(self._pt_pin))

        await asyncio.sleep(1)
        data = await self.request(session, 'initForTurntableFarm')
        lottery_times = data['remainLotteryTimes']

        if lottery_times == 0:
            println('{}, 天天抽奖次数已用完, 无法抽奖！'.format(self._pt_pin))
            return

        println('{}, 开始天天抽奖, 次数:{}'.format(self._pt_pin, lottery_times))

        for i in range(1, lottery_times + 1):
            res = await self.request(session, 'lotteryForTurntableFarm')
            println('{}, 第{}次抽奖结果:{}'.format(self._pt_pin, i, res))
            await asyncio.sleep(1)

    async def dd_park(self, session):
        """
        :param session:
        :return:
        """
        data = await self.request(session, 'ddnc_farmpark_Init', {"version": "1", "channel": 1})
        if data['code'] != '0' or 'buildings' not in data:
            println('{}, 无法获取东东乐园任务！'.format(self._pt_pin))
            return
        item_list = data['buildings']

        for idx in range(len(item_list)):
            item = item_list[idx]
            if 'topResource' not in item or 'task' not in item['topResource']:
                continue
            task = item['topResource']['task']
            if task['status'] != 1:
                println('{}, 今日已完成东东乐园:{} 浏览任务!'.format(self._pt_pin, item['name']))
                continue
            else:
                res = await self.request(session, 'ddnc_farmpark_markBrowser', {
                    "version": "1",
                    "channel": 1,
                    "advertId": task['advertId']})
                if res['code'] != '0':
                    println('{}, 无法进行东东乐园:{} 浏览任务, 原因:{}'.format(self._pt_pin, item['name'], res['message']))
                    continue
                println('{}, 正在进行东东乐园:{} 浏览任务!'.format(self._pt_pin, item['name'], task['browseSeconds']))
                await asyncio.sleep(1)
                res = await self.request(session, 'ddnc_farmpark_browseAward', {
                    "version": "1",
                    "channel": 1,
                    "advertId": task['advertId'],
                    "index": idx,
                    "type": 1
                })
                if res['code'] == '0':
                    println('{}, 领取东东乐园:{} 浏览任务奖励成功, 获得{}g水滴!'.format(self._pt_pin, item['name'],
                                                                      res['result']['waterEnergy']))
                else:
                    println('{}, 领取东东乐园:{} 浏览任务奖励失败, {}!'.format(self._pt_pin, item['name'], res['message']))

    async def do_daily_task(self, session):
        """
        领水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'taskInitForFarm')
        if data['code'] != '0':
            println('{}, 获取领水滴任务列表失败!'.format(self._pt_pin))
            return
        today_signed = data['signInit']['todaySigned']

        if not today_signed:  # 签到任务
            await self.sign(session)
        else:
            println('{}, 今日已签到, 已连续签到{}天!'.format(self._pt_pin, data['signInit']['totalSigned']))

        if not data['gotBrowseTaskAdInit']['f']:  # 浏览任务
            tasks = data['gotBrowseTaskAdInit']['userBrowseTaskAds']
            await self.do_browser_tasks(session, tasks)
        else:
            println('{}, 今日浏览广告任务已完成!'.format(self._pt_pin))

        if not data['gotThreeMealInit']['f']:  # 定时领水
            await self.timed_collar_drop(session)

        if not data['waterFriendTaskInit']['f'] and \
                data['waterFriendTaskInit']['waterFriendCountKey'] < data['waterFriendTaskInit']['waterFriendMax']:
            await self.do_friend_water(session)

        await self.get_award_of_invite_friend(session)  # 领取邀请好友奖励

        await self.clock_in(session)  # 打卡领水

        await self.water_drop_rain(session, data['waterRainInit'])  # 水滴雨

        await self.get_extra_award(session)

        await self.turntable(session)

        await self.dd_park(session)  # 东东乐园浏览领水滴

    async def get_stage_award(self, session, water_result):
        """
        领取浇水阶段性奖励
        :param session:
        :param water_result: 浇水返回的结果
        :return:
        """
        if water_result['waterStatus'] == 0 and water_result['treeEnergy'] == 10:
            award_res = await self.request(session, 'gotStageAwardForFarm', {'type': '1'})
            println('{}, 领取浇水第一阶段奖励:{}'.format(self._pt_pin, award_res))

        elif water_result['waterStatus'] == 1:
            award_res = await self.request(session, 'gotStageAwardForFarm', {'type': '2'})
            println('{}, 领取浇水第二阶段奖励:{}'.format(self._pt_pin, award_res))
        elif water_result['waterStatus'] == 2:
            award_res = await self.request(session, 'gotStageAwardForFarm', {'type': '3'})
            println('{}, 领取浇水第三阶段奖励:{}'.format(self._pt_pin, award_res))

    async def do_ten_water(self, session):
        """
        浇水10次
        :param session:
        :return:
        """
        card_data = await self.request(session, 'myCardInfoForFarm')

        for card in card_data['cardInfos']:
            if card['type'] != 'beanCard':
                continue
            if 'beanCard' not in card_data or card_data['beanCard'] < 0:
                continue
            if '限时翻倍' in card['cardSubTitle'] and JD_FARM_BEAN_CARD:
                println('{}, 您设置是是使用水滴换豆卡, 且背包有水滴换豆卡{}张, 跳过10次浇水!'.format(self._pt_pin, card_data['beanCard']))
                return

        task_data = await self.request(session, 'taskInitForFarm')

        task_limit_times = task_data['totalWaterTaskInit']['totalWaterTaskLimit']
        cur_times = task_data['totalWaterTaskInit']['totalWaterTaskTimes']

        if cur_times == task_limit_times:
            println('{}, 今日已完成十次浇水!'.format(self._pt_pin))
            return

        fruit_finished = False  # 水果是否成熟

        for i in range(cur_times, task_limit_times):
            println('{}, 开始第{}次浇水!'.format(self._pt_pin, i + 1))
            res = await self.request(session, 'waterGoodForFarm')
            if res['code'] != '0':
                println('{}, 浇水异常, 退出浇水!'.format(self._pt_pin))
                break
            println('{}, 剩余水滴:{}g!'.format(self._pt_pin, res['totalEnergy']))
            fruit_finished = res['finished']
            if fruit_finished:
                break
            if res['totalEnergy'] < 10:
                println('{}, 水滴不够10g, 退出浇水!'.format(self._pt_pin))
                break
            await self.get_stage_award(session, res)
            await asyncio.sleep(1)

        if fruit_finished:
            println('{}, 水果已可领取!'.format(self._pt_pin))

    async def get_first_water_award(self, session):
        """
        领取首次浇水奖励
        :return:
        """
        task_data = await self.request(session, 'taskInitForFarm')

        if not task_data['firstWaterInit']['f'] and task_data['firstWaterInit']['totalWaterTimes'] > 0:
            res = await self.request(session, 'firstWaterTaskForFarm')
            if res['code'] == '0':
                println('{}, 【首次浇水奖励】获得{}g水滴!'.format(self._pt_pin, res['amount']))
            else:
                println('{}, 【首次浇水奖励】领取失败, {}'.format(self._pt_pin, res))
        else:
            println('{}, 首次浇水奖励已领取!'.format(self._pt_pin))

    async def get_ten_water_award(self, session):
        """
        获取十次浇水奖励
        :param session:
        :return:
        """
        task_data = await self.request(session, 'taskInitForFarm')
        task_limit_times = task_data['totalWaterTaskInit']['totalWaterTaskLimit']
        cur_times = task_data['totalWaterTaskInit']['totalWaterTaskTimes']
        if not task_data['totalWaterTaskInit']['f'] and cur_times >= task_limit_times:
            res = await self.request(session, 'totalWaterTaskForFarm')
            if res['code'] == '0':
                println('{}, 【十次浇水奖励】获得{}g水滴!'.format(self._pt_pin, res['totalWaterTaskEnergy']))
            else:
                println('{}, 【十次浇水奖励】领取失败, {}'.format(self._pt_pin, res))

        elif cur_times < task_limit_times:
            println('{}, 【十次浇水】任务未完成, 今日浇水:{}'.format(self._pt_pin, cur_times))
        else:
            println('{}, 【十次浇水】奖励已领取!'.format(self._pt_pin))

    async def help_friend(self, session):
        """
        助力好友
        :param session:
        :return:
        """
        help_max_count = 3  # 每人每天只有三次助力机会
        cur_count = 0  # 当前已助力次数
        for code in JD_FARM_CODE:
            if cur_count >= help_max_count:
                println('{}, 今日助力次数已用完!'.format(self._pt_pin))
            if code == self._farm_info['shareCode']:
                continue
            res = await self.request(session, 'initForFarm', {
                "imageUrl": "",
                "nickName": "",
                "shareCode": code,
                "babelChannel": "3"
            })
            if 'helpResult' not in res:
                println('{}, 助力好友状态未知~'.format(self._pt_pin))
                continue
            if res['helpResult']['code'] == '0':
                println('{}, 已成功给【{}】助力!'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName']))
                println('{}, 给好友【{}】助力获得{}g水滴'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName'],
                                                      res['helpResult']['salveHelpAddWater']))
                cur_count += 1
            elif res['helpResult']['code'] == '9':
                println('{}, 之前给【{}】助力过了!'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName']))
            elif res['helpResult']['code'] == '8':
                println('{}, 今日助力次数已用完!'.format(self._pt_pin))
                break
            elif res['helpResult']['code'] == '10':
                println('{}, 好友【{}】已满五人助力!'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName']))
            else:
                println('{}, 给【{}】助力失败!'.format(self._pt_pin, res['helpResult']['masterUserInfo']['nickName']))

    async def get_water_friend_award(self, session):
        """
        领取给2未好友浇水的奖励
        :param session:
        :return:
        """
        task_data = await self.request(session, 'taskInitForFarm')
        water_friend_task_data = task_data['waterFriendTaskInit']

        if water_friend_task_data['waterFriendGotAward']:
            println('{}, 今日已领取给2位好友浇水任务奖励!'.format(self._pt_pin))
            return

        if water_friend_task_data['waterFriendCountKey'] >= water_friend_task_data['waterFriendMax']:
            res = await self.request(session, 'waterFriendGotAwardForFarm')
            if res['code'] == '0':
                println('{}, 领取给2位好友浇水任务奖励成功, 获得{}g水滴!'.format(self._pt_pin, res['addWater']))
            else:
                println('{}, 领取给2位好友浇水任务失败, {}'.format(self._pt_pin, res))

    async def click_duck(self, session):
        """
        点鸭子任务
        :return:
        """
        for i in range(10):
            data = await self.request(session, 'getFullCollectionReward', {"type": 2, "version": 14, "channel": 1,
                                                                           "babelChannel": 0})
            if data['code'] == '0':
                println('{}, {}'.format(self._pt_pin, data['title']))
            else:
                println('{}, 点鸭子次数已达上限!'.format(self._pt_pin))
                break

    async def do_ten_water_again(self, session):
        """
        再次进行十次浇水
        :param session:
        :return:
        """
        data = await self.request(session, 'initForFarm')
        total_energy = data['farmUserPro']['totalEnergy']
        println('{}, 剩余{}g水滴!'.format(self._pt_pin, total_energy))
        card_data = await self.request(session, 'myCardInfoForFarm')
        bean_card, sign_card = card_data['beanCard'], card_data['signCard'],
        double_card, fast_card = card_data['doubleCard'], card_data['fastCard']
        println('{}, 背包已有道具:\n  快速浇水卡: {}\n  水滴翻倍卡:{}\n  水滴换豆卡:{}'
                '\n  加签卡:{}'.format(self._pt_pin, fast_card, double_card, bean_card, sign_card))

        if total_energy > 100 and double_card > 0:
            for i in range(double_card):
                res = await self.request(session, 'userMyCardForFarm', {'cardType': 'doubleCard'})
                println('{}, 使用水滴翻倍卡结果:{}'.format(self._pt_pin, res))

        if sign_card > 0:
            for i in range(sign_card):
                res = await self.request(session, 'userMyCardForFarm', {'cardType': 'signCard'})
                println('{}, 使用加签卡结果:{}'.format(self._pt_pin, res))

        data = await self.request(session, 'initForFarm')
        total_energy = data['farmUserPro']['totalEnergy']

        if JD_FARM_BEAN_CARD:
            println('{}, 设置的是使用水滴换豆, 开始换豆!'.format(self._pt_pin))
            if total_energy >= 100 and card_data['beanCard'] > 0:
                res = await self.request(session, 'userMyCardForFarm', {'cardType': 'beanCard'})
                if res['code'] == '0':
                    println('{}, 使用水滴换豆卡, 获得:{}京豆!'.format(self._pt_pin, res['beanCount']))
                    return
                else:
                    println('{}, 使用水滴换豆卡, 结果:{}'.format(self._pt_pin, res))
            else:
                println('{}, 水滴不足100g, 无法使用水滴换豆卡!'.format(self._pt_pin))

        #  可用水滴
        available_water = total_energy - JD_FARM_RETAIN_WATER

        if available_water < 10:
            println('{}, 当前可用水滴(=当前剩余水滴{}g-保留水滴{}g)不足10g, 无法浇水!'.format(self._pt_pin, total_energy,
                                                                        JD_FARM_RETAIN_WATER))
            return

        for i in range(int(available_water / 10)):
            res = await self.request(session, 'waterGoodForFarm')
            if res['code'] == '0':
                println('{}, 浇水10g, 距水果成熟还需浇水{}g!'.format(self._pt_pin,
                                                          self._farm_info['treeTotalEnergy'] - res['treeEnergy']))
                if res['finished']:  # 水果成熟了不需要再浇水
                    break
            else:
                println('{}, 浇水失败, 不再浇水!'.format(self._pt_pin))
                break

    async def get_share_code(self):
        """
        获取助力码
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            farm_info = await self.init_for_farm(session=session)
            if not farm_info:
                return None
            println('{}, 助力码:{}'.format(self._pt_pin, farm_info['shareCode']))
            return farm_info['shareCode']

    async def notify_result(self, session):
        """
        通知结果
        :param session:
        :return:
        """
        farm_data = await self.request(session, 'initForFarm')
        farm_task_data = await self.request(session, 'taskInitForFarm')
        today_water_times = farm_task_data['totalWaterTaskInit']['totalWaterTaskTimes']
        message = '【活动名称】东东农场\n【京东账号】{}\n【今日共浇水】{}次\n'.format(self._pt_pin, today_water_times)
        message += '【奖品名称】{}\n'.format(self._farm_info['name'])
        message += '【剩余水滴】{}g💧\n'.format(farm_data['farmUserPro']['totalEnergy'])
        if farm_data['farmUserPro']['treeTotalEnergy'] == farm_data['farmUserPro']['treeEnergy']:
            message += '【水果进度】已成熟, 请前往东东农场领取并种植新的水果!\n'
        else:
            message += '【完整进度】{}%, 已浇水{}次!\n'.format(
                round(farm_data['farmUserPro']['treeEnergy'] / farm_data['farmUserPro']['treeTotalEnergy'] * 100, 2),
                math.ceil(farm_data['farmUserPro']['treeEnergy'] / 10),
            )
            if farm_data['toFlowTimes'] > farm_data['farmUserPro']['treeEnergy'] / 10:
                message += '【开花进度】再浇水{}次开花\n'.format(
                    farm_data['toFlowTimes'] - int(farm_data['farmUserPro']['treeEnergy'] / 10))
            elif farm_data['toFruitTimes'] > farm_data['farmUserPro']['treeEnergy'] / 10:
                message += '【结果进度】再浇水{}次结果\n'.format(
                    farm_data['toFruitTimes'] - int(farm_data['farmUserPro']['treeEnergy'] / 10)
                )

            remain_water_times = (farm_data['farmUserPro']['treeTotalEnergy'] - farm_data['farmUserPro']['treeEnergy']
                                  - farm_data['farmUserPro']['totalEnergy']) / 10
            message += '【预测】{}天后可以领取水果!\n'.format(math.ceil(remain_water_times / today_water_times))

        message += '【活动入口】京东APP->我的->东东农场\n'

        self._message = message

    async def got_water(self, session):
        """
        领取水滴
        :param session:
        :return:
        """
        data = await self.request(session, 'gotWaterGoalTaskForFarm',
                                  {"type": 3, "version": 14, "channel": 1, "babelChannel": 0})
        println('{}, 领取水滴:{}!'.format(self._pt_pin, data))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self._cookies, headers=self.headers) as session:
            self._farm_info = await self.init_for_farm(session=session)
            if not self._farm_info:
                println('{}, 无法获取农场数据, 退出程序!'.format(self._pt_pin))
                return
            await self.help_friend(session)  # 助力好友
            await self.do_daily_task(session)  # 每日任务
            await self.do_ten_water(session)  # 浇水十次
            await self.get_first_water_award(session)  # 领取首次浇水奖励
            await self.get_ten_water_award(session)  # 领取十次浇水奖励
            await self.get_water_friend_award(session)  # 领取给好友浇水的奖励
            await self.click_duck(session)  # 点鸭子任务
            await self.do_ten_water_again(session)  # 再次浇水
            await self.got_water(session)  # 领水滴
            await self.notify_result(session)  # 结果通知


def start(pt_pin, pt_key, name='东东农场'):
    """
    程序入口
    :param name:
    :param pt_pin:
    :param pt_key:
    :return:
    """
    try:
        app = JdFarm(pt_pin, pt_key)
        asyncio.run(app.run())
        return app.message
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    from utils.process import process_start
    process_start(start, '东东农场')
