#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/14 14:38
# @File    : jd_sign_collection.py
# @Project : jd_scripts
# @Desc    : 京东签到合集
import os
import json
import asyncio
import sys
import time

import aiohttp


from log import get_logger

logger = get_logger('jd_sign_collection')


class JdSignCollection:

    def __init__(self, pt_pin='', pt_key=''):
        self._pt_pin = pt_pin
        self._pt_key = pt_key

    async def jd_bean(self, session):
        """
        京东京豆签到
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/client.action'
        data = {
            'functionId': 'signBeanIndex',
            'appid': 'ld'
        }
        response = await session.post(url, data=data)
        text = await response.text()
        data = json.loads(text)
        if data['code'] == '0':
            if data['data']['dailyAward']['type'] == '1':
                bean_count = data['data']['dailyAward']['beanAward']['beanCount']
                logger.info('今日已签到, 已获得{}京豆'.format(bean_count))
        elif data['code'] == '3':
            logger.info("账号:{}, Cookie已过期, 请重新获取".format(self._pt_pin))
        else:
            logger.info("京东签到异常")

    async def jd_store(self, session):
        """
        京东超市签到
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/api?appid=jdsupermarket&functionId=smtg_sign&clientVersion=8.0.0&client=m&body' \
              '=%7B%7D'
        session.headers.add('Origin', 'https://jdsupermarket.jd.com')
        response = await session.get(url)
        text = await response.text()
        data = json.loads(text)
        if data['data']['success']:
            logger.info("签到成功")
        else:
            logger.info(data['data']['bizMsg'])

    async def jr_steel(self, session):
        """
        金融钢镚
        :param session:
        :return:
        """
        url = 'https://ms.jr.jd.com/gw/generic/hy/h5/m/signIn1?_={}'.format(int(time.time()*1000))
        session.headers.add('Referer', 'https://member.jr.jd.com/activities/sign/v5/indexV2.html?channelLv=lsth')
        session.headers.add('Content-type', 'application/x-www-form-urlencoded;charset=UTF-8')
        body = 'reqData=%7B%22videoId%22%3A%22311372930347370496%22%2C%22channelSource%22%3A%22JRAPP6.0%22%2C' \
               '%22channelLv%22%3A%22lsth%22%2C%22riskDeviceParam%22%3A%22%7B%7D%22%7D'
        response = await session.post(url=url, data=body)
        text = await response.text()
        data = json.loads(text)
        logger.info('金融钢镚: ' + data['resultData']['resBusiMsg'])


    async def jd_turn(self, session):
        """
        京东转盘
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=wheelSurfIndex&body=%7B%22actId%22%3A%22jgpqtzjhvaoym%22' \
              '%2C%22appSource%22%3A%22jdhome%22%7D&appid=ld'
        response = await session.get(url)
        text = await response.text()
        data = json.loads(text)
        if 'lotteryCode' in data['data']:
            logger.info('京东转盘查询成功')
        else:
            logger.info('京东转盘查询失败')

    async def jd_flash_sale(self, session):
        """
        京东闪购
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=partitionJdSgin&clientVersion=10.0.4&partner=jingdong' \
              '&sign=4ede62576bdf67ef8a5488a66e275460&sv=101&client=android&st=1623675187639&uuid=a27b83d3d1dba1cc'
        body = 'body=%7B%22version%22%3A%22v2%22%7D&'
        session.headers.add('Content-type', 'application/x-www-form-urlencoded;charset=UTF-8')
        response = await session.post(url=url, data=body)
        text = await response.text()
        data = json.loads(text)
        logger.info(data['result']['msg'])

    async def jd_cash(self, session):
        """
        京东现金红包
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=pg_interact_interface_invoke&clientVersion=10.0.4&build' \
               '=88623&partner=jingdong&openudid=a27b83d3d1dba1cc&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&uts' \
               '=0f31TVRjBSsqndu4' \
               '%2FjgUPz6uymy50MQJBfnveeoiuNIbXyekvS9ORCSuomai1WQY0wdhG3U33LUq1bIOeJvrjVSe2OAzV8d0c9a' \
               '%2FxxjDubHoGvngh9behA5mRI%2FtJiit%2BOS4ZUfZeP6Z3iJ4BHAnX3gCJK7oGMl' \
               '%2BWRgKLncGjLTENZKciedrOekRwVutgFkgFdY1%2FJCmMNaHwC9zD3xT9g%3D%3D&st=1623675622893&sign' \
               '=78b531002169e564d30e18ef35507d3a&sv=120&client=android&body=%7B%22argMap%22%3A%7B%22currSignCursor' \
               '%22%3A1%7D%2C%22dataSourceCode%22%3A%22signIn%22%2C%22floorToken%22%3A%22caabe244-5288-4029-b533' \
               '-4e5a9a5ff284%22%7D'
        response = await session.get(url)
        text = await response.text()
        data = json.loads(text)
        if data['success']:
            logger.info('现金红包签到成功')
        else:
            logger.info('现金红包签到失败, 原因:{}'.format(data['message']))
            logger.info('当日已签到之后, 也会提示活动太火爆!')

    async def jd_magic_cube(self, session):
        """
        京东小魔方
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=getNewsInteractionInfo&appid=smfe${sign?`&body=${encodeURIComponent(`{"sign":${sign}}`)}`:``}'

    async def jd_subsidy(self, session):
        """
        京东金贴
        :param session:
        :return:
        """
        pass

    async def jd_get_cash(self, session):
        """
        京东领现金
        :return:
        """
        pass

    async def jd_shake(self, session):
        """
        京东摇一摇
        :param session:
        :return:
        """
        pass

    async def jd_killing(self, session):
        """
        京东秒杀
        :param session:
        :return:
        """
        pass

    async def jd_wonderful(self, session):
        """
        京东精彩
        :return:
        """
        pass

    async def jd_car(self, session):
        """
        京东汽车
        :param session:
        :return:
        """
        pass

    async def jr_doll(self, session):
        """
        京东金融
        :param session:
        :return:
        """
        pass

    async def jd_shop_card(self, session):
        """
        京东商城-卡包
        :param session:
        :return:
        """
        pass

    async def jd_shop_undies(self, session):
        """
        京东商城-内衣
        :param session:
        :return:
        """
        pass

    async def jd_shop_gaming(self, session):
        """
        京东商城-电竞
        :param session:
        :return:
        """
        pass

    async def jd_shop_suitcase(self, session):
        """
        京东商城-箱包
        :param session:
        :return:
        """
        pass

    async def jd_shop_clothing(self, session):
        """
        京东商城-服饰
        :param session:
        :return:
        """
        url = 'https://api.m.jd.com/client.action?functionId=userSign&clientVersion=10.0.4&build=88623&client=android&partner=jingdong&openudid=a27b83d3d1dba1cc&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&st=1623676827399&sign=e5ade7bdef2dc229fcaf99074221b9e9&sv=102'
        body = 'body=%7B%22geo%22%3A%7B%22lat%22%3A%2223.013085%22%2C%22lng%22%3A%22113.390073%22%7D%2C%22params%22' \
               '%3A%22%7B%5C%22enActK%5C%22%3A%5C%229wKIMMJjQLbQFeZ6KQv0JbC8SX4n0baClTvTUvkZEmnQN9WZKJiacLlvx6' \
               '%2F9Y1HvcRRfojzJNzI1%5C%5Cn8%2F1kQqsYsbbH43AGnA2%2FKyDbkvDgi7euV3a8HzyG%2F8ICGuGbpGLv%5C%22%2C%5C' \
               '%22isFloatLayer%5C%22%3Afalse%2C%5C%22ruleSrv%5C%22%3A%5C%2200839807_48244249_t1%5C%22%2C%5C%22signId' \
               '%5C%22%3A%5C%22LaYAPPYx%2BP8aZs%2Fn4coLNw%3D%3D%5C%22%7D%22%2C%22riskParam%22%3A%7B%22eid%22%3A' \
               '%22eidA1a01812289s8Duwy8MyjQ9m%2FiWxzcoZ6Ig7sNGqHp2V8%2FmtnOs' \
               '%2BKCpWdqNScNZAsDVpNKfHAj3tMYcbWaPRebvCS4mPPRels2DfOi9PV0J%2B%2FZRhX%22%2C%22pageClickKey%22%3A' \
               '%22Babel_Sign%22%2C%22shshshfpb%22%3A%22qyIEXXcEj%2Bo%2FT7BgWolC5HlcQo72LyOIHBAzbP9RRfNAF0fE2O' \
               '%2BrRDcHKypk6KjymAjpzPn41lYuOZuFC2hkjFw%3D%3D%22%7D%7D'
        session.headers.add('Content-type', 'application/x-www-form-urlencoded;charset=UTF-8')
        response = await session.post(url=url, data=body)
        text = await response.text()
        print(text)

    async def jd_shop_school(self, session):
        """
        京东商城-学校
        :param session:
        :return:
        """
        pass

    async def jd_shop_health(self, session):
        """
        京东商城-健康
        :param session:
        :return:
        """
        pass

    async def jd_shop_shoes(self, session):
        """
        京东商城-鞋装
        :param session:
        :return:
        """
        pass

    async def jd_shop_child(self, session):
        """
        京东商城-童装
        :param session:
        :return:
        """
        pass

    async def js_shop_baby(self, session):
        """
        京东商城-母婴
        :param session:
        :return:
        """
        pass

    async def js_shop_3c(self, session):
        """
        京东商城-数码
        :param session:
        :return:
        """
        pass

    async def js_shop_women(self, session):
        """
        京东商城-女装
        :param session:
        :return:
        """
        pass

    async def jd_shop_book(self, session):
        """
        京东商城-图书
        :param session:
        :return:
        """
        pass

    async def jd_pat(self, session):
        """
        京东拍拍-二手
        :param session:
        :return:
        """
        pass

    async def jd_shop_food_market(self, session):
        """
        京东商城-菜场
        :param session:
        :return:
        """
        pass

    async def jd_shop_accompany(self, session):
        """
        京东商城-陪伴
        :param session:
        :return:
        """
        pass

    async def jd_live(self, session):
        """
        京东智能-生活
        :param session:
        :return:
        """
        pass

    async def jd_shop_clean(self, session):
        """
        京东商城-清洁
        :param session:
        :return:
        """
        pass

    async def jd_shop_care(self, session):
        """
        京东商城-个护
        :param session:
        :return:
        """
        pass

    async def jd_shop_jewels(self, session):
        """
        京东商城-珠宝
        :param session:
        :return:
        """
        pass

    async def jr_bean_double(self, session):
        """
        金融金豆-双签
        :param session:
        :return:
        """
        pass

    async def start(self):
        cookies = {
            'pt_pin': self._pt_pin,
            'pt_key': self._pt_key,
        }
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) Mobile/16D57 ',
        }
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            # await self.jd_bean(session)   # 京东京豆
            # await self.jd_store(session)  # 京东超市
            # await self.jr_steel(session)  # 金融钢镚
            # await self.jd_turn(session)   # 京东转盘
            # await self.jd_flash_sale(session)  # 京东闪购
            # await self.jd_cash(session)  # 京东领现金
            # await self.jd_shop_clothing(session) # 京东服饰, 有签名暂时无解
            # await self.jd_shop_gaming(session) # 京东电竞, 有签名暂时无解
            await self.jd_bean(session)

def start():

    logger.info("开始京东多合一签到")
    jd_cookies = os.getenv('JD_COOKIES', None)
    if not jd_cookies:
        logger.info("未设置JD_COOKIES环境变量, 退出程序")
        return
    jd_cookie_list = jd_cookies.split('&')

    for jd_cookie in jd_cookie_list:
        values = jd_cookie.split(';')
        if len(values) != 2:
            logger.info("提供的JD_COOKIES有误, 请检查配置")
            return
        _, pt_pin = values[0].split('=')
        _, pt_key = values[1].split('=')
        app = JdSignCollection(pt_pin, pt_key)
        asyncio.run(app.start())


if __name__ == '__main__':
    start()
