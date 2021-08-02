#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/29 10:34 上午
# @File    : jd_grab_bean.py
# @Project : jd_scripts
# @Cron    : #3 */16 * * *
# @Desc    : 京东APP->首页->领京豆->抢京豆
import aiohttp
import asyncio
import json
from config import USER_AGENT, JD_GRAB_BEAN_CODE
from urllib.parse import unquote, urlencode
from utils.console import println
from utils.wraps import jd_init


@jd_init
class JdGrabBean:
    """
    抢京豆
    """
    headers = {
        'user-agent': USER_AGENT,
        'referer': 'https://h5.m.jd.com/rn/3MQXMdRUTeat9xqBSZDSCCAE9Eqz/index.html',

    }

    async def request(self, session, function_id, body=None, method='GET'):
        """
        :param session:
        :param function_id:
        :param body:
        :param method:
        :return:
        """
        try:
            if not body:
                body = {}
            params = {
                'functionId': function_id,
                'appid': 'ld',
                'client': 'android',
                'clientVersion': '10.0.10',
                'networkType': 'wifi',
                'osVersion': '',
                'uuid': '',
                'jsonp': '',
                'body': json.dumps(body),
            }
            url = 'https://api.m.jd.com/client.action?' + urlencode(params)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)
            await asyncio.sleep(0.5)
            text = await response.text()
            data = json.loads(text)
            return data

        except Exception as e:
            println('{}, 获取数据失败,{}!'.format(self.account, e.args))
            return {
                'code': 9999
            }

    async def _get_index_data(self, session):
        """
        获取首页数据
        :param session:
        :return:
        """
        res = await self.request(session, 'signBeanGroupStageIndex',
                                 {"monitor_refer": "", "rnVersion": "3.9", "fp": "-1", "shshshfp": "-1",
                                  "shshshfpa": "-1", "referUrl": "-1", "userAgent": "-1", "jda": "-1",
                                  "monitor_source": "bean_m_bean_index"})
        if res['code'] != '0':
            println('{}, 获取首页数据失败!'.format(self.account))
            return None
        return res['data']

    async def get_share_code(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:

            data = await self._get_index_data(session)
            if 'groupCode' not in data:
                println('{}, 未组团, 去分享!'.format(self.account))
                await self.request(session, 'signGroupHit', {'activeType': data['activityType']})
                await asyncio.sleep(1)
                data = await self._get_index_data(session)

            if not data:
                println('{}, 获取助力码失败!'.format(self.account))
                return None

            body = {
                'activeType': data['activityType'],
                'groupCode': data['groupCode'],
                'shareCode': data['shareCode'],
                'activeId': str(data['activityMsg']['activityId']),
                "source": "guest"
            }
            code = json.dumps(body)
            println('{}, 助力码: {}'.format(self.account, code))
            return code

    async def help(self, session):
        """
        :return:
        """
        println('{}, 开始助力好友...'.format(self.account))
        for code in JD_GRAB_BEAN_CODE:
            try:
                params = json.loads(code)
                res = await self.request(session, 'signGroupHelp', params)
                if res['code'] != '0' or res['data']['helpToast'] != '助力成功':
                    msg = res['data']['popInfo']['popMsg']
                    println('{}, {}'.format(self.account, msg))
                    if '上限' in msg:
                        break
                    if '没有有效' in msg:
                        break
            except Exception as e:
                println('{}, 助力好友失败, {}!'.format(self.account, e.args))
                continue
        println('{}, 完成好友助力...'.format(self.account))

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            await self.help(session)


if __name__ == '__main__':
    from utils.process import process_start
    process_start(JdGrabBean, '抢京豆', process_num=1)

