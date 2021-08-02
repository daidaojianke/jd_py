#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/2 下午9:50
# @Project : jd_scripts
# @File    : jd_amusement_post.py
# @Cron    : 45 8 * * *
# @Desc    : 京小鸽游乐寄
import asyncio
import json

import ujson
import aiohttp
from config import USER_AGENT

from utils.wraps import jd_init
from utils.console import println


@jd_init
class JdAmusementPost:
    """
    京小鸽游乐寄
    """
    headers = {
        'origin': 'https://jingcai-h5.jd.com',
        'user-agent': 'jdapp;' + USER_AGENT,
        'lop-dn': 'jingcai.jd.com',
        'accept': 'application/json, text/plain, */*',
        'appparams': '{"appid":158,"ticket_type":"m"}',
        'content-type': 'application/json',
        'referer': 'https://jingcai-h5.jd.com/index.html'
    }

    async def request(self, session, path, body=None, method='POST'):
        """
        请求数据
        :return:
        """
        try:
            if not body:
                body = {}
            url = 'https://lop-proxy.jd.com/' + path
            if method == 'POST':
                response = await session.post(url, json=body)
            else:
                response = await session.get(url, json=body)

            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            println('{}, 请求服务器数据失败, {}'.format(self.account, e.args))
            return {
                'success': False
            }

    async def get_index_data(self, session):
        """
        获取首页数据
        :return:
        """
        res = await self.request(session, 'MangHeApi/queryRuleInfo', [{
            "userNo": "$cooMrdGatewayUid$"
        }])
        success = res.get('success', False)
        if not success:
            return None
        return res['content']

    async def get_card(self, session, code):
        """
        领取卡片
        :param code:
        :param session:
        :return:
        """
        body = [{
            "userNo": "$cooMrdGatewayUid$",
            "getCode": code,
        }]
        res = await self.request(session, 'MangHeApi/getCard', body)
        success = res.get('success', False)
        if success:
            println('{}, 成功领取1张卡片!'.format(self.account))
        else:
            println('{}, 领取卡片失败!'.format(self.account))

    async def sign(self, session):
        """
        每日签到
        :param session:
        :return:
        """
        res = await self.request(session, '/mangHeApi/signIn', [{
            "userNo": "$cooMrdGatewayUid$"
        }])
        success = res.get('success', False)
        if not success:
            println('{}, 签到失败, {}!'.format(self.account, res.get('msg', '原因未知')))
        else:
            println('{}, 签到成功!'.format(self.account))

    async def visit_jc(self, session):
        """
        访问精彩
        :param session:
        :return:
        """
        body = [{
            "userNo": "$cooMrdGatewayUid$"
        }]
        await self.request(session, 'mangHeApi/setUserHasView', body)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies,
                                         json_serialize=ujson.dumps) as session:
            data = await self.get_index_data(session)
            if not data:
                println('{}, 无法获取活动首页数据, 退出!'.format(self.account))
                return
            for item in data:
                if item['status'] == 10:
                    println('{}, 今日已领取过《{}》的卡片!'.format(self.account, item['name']))
                    continue
                jump_type = item.get('jumpType')
                if jump_type == 41:
                    await self.visit_jc(session)
                    await asyncio.sleep(1)
                elif jump_type == 31:
                    await self.sign(session)
                    await asyncio.sleep(1)
            data = await self.get_index_data(session)

            for item in data:
                if item['status'] == 11:
                    await self.get_card(session, item['getRewardNos'][0])


if __name__ == '__main__':
    # from config import JD_COOKIES
    # app = JdAmusementPost(**JD_COOKIES[0])
    # asyncio.run(app.run())

    from utils.process import process_start
    process_start(JdAmusementPost, '京小鸽-游乐寄')
