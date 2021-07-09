#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/21 21:47
# @File    : jd_planting_bean.py
# @Project : jd_scripts
# @Desc    : 种豆得豆
import asyncio
import json
from functools import wraps
from urllib.parse import unquote, quote

import aiohttp
from furl import furl
from utils.console import println
from utils.logger import logger
from utils.process import process_start
from utils.notify import notify
from config import USER_AGENT, JD_PLANTING_BEAN_CODE


def println_task(func=None):
    """
    输出任务
    :param func:
    :return:
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        task = args[-1]
        if task['isFinished'] or (int(task['totalNum']) - int(task['gainedNum']) == 0):  # 今天已经完成任务了！
            println('{}, 任务:{}, 今日已完成过或已达到上限, 不需要重复执行！'.format(task['account'], task['taskName']))
            return

        if task['taskType'] == 8:  # 评价商品任务
            println('{}, 任务:{}, 请手动到APP中完成！'.format(task['account'], task['taskName']))
            return

        println('{}, 开始做{}任务!'.format(task['account'], task['taskName']))
        res = await func(*args, **kwargs)
        println('{}, 已完成{}任务!'.format(task['account'], task['taskName']))
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
        self._cur_round_list = None
        self._prev_round_list = None
        self._task_list = None  # 任务列表
        self._nickname = None  # 京东昵称
        self._message = ''
        self._share_code = None

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
            await asyncio.sleep(1)
            logger.info('种豆得豆:{}'.format(text))
            data = json.loads(text)
            return data

        except Exception as e:
            logger.error('{}, 种豆得豆访问服务器失败:[function_id={}], 错误信息:{}'.format(self._account, function_id, e.args))

    async def get(self, session, function_id, body=None, wait_time=1):
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
            if wait_time > 0:
                await asyncio.sleep(1)
            return data

        except Exception as e:
            logger.error('{}, 种豆得豆访问服务器失败:[function_id={}], 错误信息:{}'.format(self._account, function_id, e.args))

    async def planting_bean_index(self, session):
        """
        :return:
        """
        data = await self.post(session=session, function_id='plantBeanIndex')

        if not data or data['code'] != '0' or 'errorMessage' in data:
            println('{},访问种豆得豆首页失败, 退出程序！错误原因:{}'.format(self._account, data))
            return False
        data = data['data']

        round_list = data['roundList']
        self._cur_round_id = round_list[1]['roundId']
        self._task_list = data['taskList']
        self._cur_round_list = round_list[1]
        self._prev_round_list = round_list[0]
        self._message = '\n【活动名称】种豆得豆\n'
        self._message += f"【京东昵称】:{data['plantUserInfo']['plantNickName']}\n"
        self._message += f'【上期时间】:{round_list[0]["dateDesc"].replace("上期 ", "")}\n'
        self._message += f'【上期成长值】:{round_list[0]["growth"]}\n'
        return True

    async def receive_nutrient(self, session):
        """
        收取营养液
        :param session:
        :return:
        """
        println('{}, 开始收取营养液!'.format(self._account))
        data = await self.post(session, 'receiveNutrients',
                               {"roundId": self._cur_round_id, "monitor_refer": "plant_receiveNutrients"})
        println('{}, 完成收取营养液, {}'.format(self._account, data))

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
        println('{}, 收取营养液:{}'.format(self._account, data))

    @println_task
    async def visit_shop_task(self, session, task):
        """
        浏览店铺任务
        :param session:
        :param task:
        :return:
        """
        shop_data = await self.get(session, 'shopTaskList', {"monitor_refer": "plant_receiveNutrients"})
        if shop_data['code'] != '0':
            println('{}, 获取{}任务失败!'.format(self._account, task['taskName']))

        shop_list = shop_data['data']['goodShopList'] + shop_data['data']['moreShopList']
        for shop in shop_list:
            body = {
                "monitor_refer": "plant_shopNutrientsTask",
                "shopId": shop["shopId"],
                "shopTaskId": shop["shopTaskId"]
            }
            data = await self.get(session, 'shopNutrientsTask', body)
            if data['code'] == '0' and 'data' in data:
                println('{}, 浏览店铺结果:{}'.format(self._account, data['data']))
            else:
                println('{}, 浏览店铺结果:{}'.format(self._account, data['errorMessage']))
            await asyncio.sleep(1)

    @println_task
    async def pick_goods_task(self, session, task):
        """
        挑选商品任务
        :return:
        """
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
                    println('{}, {}'.format(self._account, res['errorMessage']))
                else:
                    println('{}, {}'.format(self._account, res))

                await asyncio.sleep(1)

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
            println('{}, 获取关注频道任务列表失败!'.format(self._account))
            return
        data = data['data']
        channel_list = data['goodChannelList'] + data['normalChannelList']

        for channel in channel_list:
            body = {
                "channelId": channel['channelId'],
                "channelTaskId": channel['channelTaskId']
            }
            res = await self.get(session, 'plantChannelNutrientsTask', body)
            if 'errorCode' in res:
                println('{}, 关注频道结果:{}'.format(self._account, res['errorMessage']))
            else:
                println('{}, 关注频道结果:{}'.format(self._account, res))
            await asyncio.sleep(1)

    async def get_friend_nutriments(self, session, page=1):
        """
        获取好友营养液
        :param page:
        :param session:
        :return:
        """
        if page > 3:
            return
        println('{}, 开始收取第{}页的好友营养液!'.format(self._account, page))
        body = {
            'pageNum': str(page),
        }
        data = await self.post(session, 'plantFriendList', body)

        if data['code'] != '0' or 'data' not in data:
            println('{}, 无法获取好友列表!'.format(self._account))
            return

        data = data['data']
        msg = None

        if 'tips' in data:
            println('{}, 今日偷取好友营养液已达上限!'.format(self._account))
            return
        if 'friendInfoList' not in data or len(data['friendInfoList']) < 0:
            println('{}, 当前暂无可以获取的营养液的好友！'.format(self._account))
            return

        for item in data['friendInfoList']:
            if 'nutrCount' not in item or int(item['nutrCount']) <= 1:  # 小于两瓶基本无法活动奖励, 不收
                continue
            body = {
                'roundId': self._cur_round_id,
                'paradiseUuid': item['paradiseUuid']
            }
            res = await self.post(session, 'collectUserNutr', body)
            if res['code'] != '0' or 'errorMessage' in res:
                println('{}, 帮:{}收取营养液失败!'.format(self._account, item['plantNickName']))
                continue

            msg = '{}, 成功帮{}收取{}瓶营养液, '.format(self._account, item['plantNickName'], res['data']['friendNutrRewards'])
            if int(res['data']['collectNutrRewards']) > 0:
                msg += '恭喜获得{}瓶奖励!'.format(res['data']['collectNutrRewards'])
            else:
                msg += '您暂未活动奖励！'
            println(msg)
            await asyncio.sleep(0.5)  # 短暂延时，避免出现活动火爆

        if not msg:
            println('{}, 第{}页好友没有可收取的营养液!'.format(self._account, page))

        await asyncio.sleep(1)
        await self.get_friend_nutriments(session, page+1)

    @println_task
    async def evaluation_goods_task(self, session, task):
        """
        :param session:
        :param task:
        :return:
        """
        println('{}, 任务:{}, 请手动前往APP完成任务！'.format(self._account, task['taskName']))

    @println_task
    async def visit_meeting_place_task(self, session, task):
        """
        逛会场
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '4'})
        println('{}, {}:{}'.format(self._account, task['taskName'], data))

    @println_task
    async def free_fruit_task(self, session, task):
        """
        免费水果任务
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '36'})
        println('{}, {}:{}'.format(self._account, task['taskName'], data))

    @println_task
    async def jx_red_packet(self, session, task):
        """
        京喜红包
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '33'})
        println('{}, {}:{}'.format(self._account, task['taskName'], data))

    @println_task
    async def double_sign_task(self, session, task):
        """
        京喜双签
        :param session:
        :param task:
        :return:
        """
        data = await self.post(session, 'receiveNutrientsTask', {"awardType": '7'})
        println('{}, {}:{}'.format(self._account, task['taskName'], data))

    async def get_share_code(self):
        """
        获取当前账号的助力码
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            data = await self.get(session, 'plantSharePageIndex', {'roundId': ''}, wait_time=0)
            if data['code'] != '0':
                return None
            share_url = furl(data['data']['jwordShareInfo']['shareUrl'])
            share_code = share_url.args.get('plantUuid', '')
            println('{} 助力码:{}'.format(self._account, share_code))
            return share_code

    @println_task
    async def help_friend_task(self, session, task):
        """
        助力好友任务
        :param session:
        :param task:
        :return:
        """
        println('开始助力{}的好友, 如有剩余助力将助力作者!'.format(self._account))
        for planting_code in JD_PLANTING_BEAN_CODE:
            if self._share_code == planting_code:  # 跳过自己的助力码
                continue
            println('{}, 开始助力好友:{}'.format(self._account, planting_code))
            body = {
                "plantUuid": planting_code,
                "wxHeadImgUrl": "",
                "shareUuid": "",
                "followType": "1",
            }
            data = await self.post(session, 'plantBeanIndex', body)
            if data['code'] == '0':
                if data['data']['helpShareRes']['state'] == '2':
                    println('{}, 助力结果:{}'.format(self._account, '您今日助力的机会已耗尽，已不能再帮助好友助力了!'))
                elif data['data']['helpShareRes']['state'] == '3':
                    println('{}, 助力结果:{}'.format(self._account, '该好友今日已满9人助力/20瓶营养液,明天再来为Ta助力吧'))
                else:
                    println('{}, 助力结果:{}'.format(self._account, data['data']['helpShareRes']['promptText']))
            else:
                println('{}, 助力结果:{}'.format(self._account, '无法为该好友助力！'))

    async def do_tasks(self, session):
        """
        做任务
        :param session:
        :return:
        """
        task_map = {
            1: self.receive_nutrient_task,  # 每日签到
            2: self.help_friend_task,  # 助力好友
            3: self.visit_shop_task,  # 浏览店铺
            # 4: self.visit_meeting_place_task,  # 逛逛会场
            5: self.pick_goods_task,  # 挑选商品
            #7: self.double_sign_task,  # 金融双签
            8: self.evaluation_goods_task,  # 评价商品,
            10: self.focus_channel_task,  # 关注频道,
            33: self.jx_red_packet,  # 京喜红包
            36: self.free_fruit_task  # 免费水果

        }
        for task in self._task_list:
            if task['isFinished'] == 1:
                println('{}, 任务:{}, 今日已领取过奖励, 不再执行...'.format(self._account, task['taskName']))
                continue
            if task['taskType'] in task_map:
                task['account'] = self._account
                await task_map[task['taskType']](session, task)
            else:
                data = await self.post(session, 'receiveNutrientsTask', {"awardType": str(task['taskType'])})
                println('{}, {}:{}'.format(self._account, task['taskName'], data))

    async def collect_nutriments(self, session):
        """
        收取营养液
        :return:
        """
        # 刷新数据
        await self.planting_bean_index(session)
        if not self._cur_round_list or 'roundState' not in self._cur_round_list:
            println('{}, 获取营养池数据失败, 无法收取！'.format(self._account))

        if self._cur_round_list['roundState'] == '2':
            for item in self._cur_round_list['bubbleInfos']:
                body = {
                    "roundId": self._cur_round_id,
                    "nutrientsType": item['nutrientsType'],
                }
                res = await self.post(session, 'cultureBean', body)
                println('{}, 收取-{}-的营养液, 结果:{}'.format(self._account, item['name'], res))
                await asyncio.sleep(1)
            println('{}, 收取营养液完成！'.format(self._account))
        else:
            println('{}, 暂无可收取的营养液！'.format(self._account))

    async def get_reward(self, session):
        """
        获取奖励
        :param session:
        :return:
        """
        await self.planting_bean_index(session)

        if not self._prev_round_list:
            println('{}, 无法获取上期活动信息!'.format(self._account))

        if self._prev_round_list['awardState'] == '6':
            self._message += '【上期兑换京豆】{}个!\n'.format(self._prev_round_list['awardBeans'])
        elif self._prev_round_list['awardState'] == '4':
            self._message += '【上期状态】{}\n'.format(self._prev_round_list['tipBeanEndTitle'])
        elif self._prev_round_list['awardState'] == '5':
            println('{}, 开始领取京豆!'.format(self._account))
            body = {
                "roundId": self._prev_round_list['roundId']
            }
            res = await self.post(session, 'receivedBean', body)
            if res['code'] != '0':
                self._message += '【上期状态】查询异常:{}\n'.format(self._prev_round_list)
            else:
                self._message += '【上期兑换京豆】{}个\n'.format(res['data']['awardBean'])
        else:
            self._message += '【上期状态】查询异常:{}\n'.format(self._prev_round_list)

        self._message += f'【本期时间】:{self._cur_round_list["dateDesc"].replace("上期 ", "")}\n'
        self._message += f'【本期成长值】:{self._cur_round_list["growth"]}\n'

        println(self._message)
        notify(self._message)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            is_success = await self.planting_bean_index(session)
            if not is_success:
                println('{}, 无法获取活动数据!'.format(self._account))
                return
            self._share_code = await self.get_share_code()  # 获取当前账号助力码
            await self.receive_nutrient(session)
            await self.do_tasks(session)
            await self.get_friend_nutriments(session)
            await self.collect_nutriments(session)
            await self.get_reward(session)


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdPlantingBean(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    process_start(start, '种豆得豆')
