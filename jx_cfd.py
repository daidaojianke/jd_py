#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/12 下午9:16 
# @File    : jx_cfd.py
# @Project : jd_scripts
# @Cron    : #
# @Desc    : 京喜财富岛
import json
import re
import time

import aiohttp
import asyncio
from urllib.parse import unquote

from utils.console import println


def get_timestamp():
    """
    获取当前时间戳
    """
    return int(time.time()*100)


class JxCfd:

    headers = {
        'User-Agent': 'jdpingou;iPhone;12.0.1;15.1.1;network/wifi;Mozilla/5.0'
                      ' (iPhone; CPU iPhone OS 15_1_1 like Mac OS X) AppleWebKit/605.1.15'
                      ' (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1',
        'Referer': 'https://st.jingxi.com/fortune_island/index2.html?ptag=7155.9.47&sceneval=2',
    }

    def __init__(self, pt_pin, pt_key):

        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }

        self._pt_pin = unquote(pt_pin)

    async def request(self, session, url, method='GET'):
        """
        发起请求
        """
        try:
            if method == 'GET':
                response = await session.get(url=url)
            else:
                response = await session.post(url=url)

            text = await response.text()
            temp = re.search(r'\((.*)', text).group(1)
            data = json.loads(temp)
            return data

        except Exception as e:
            println('{}, 访问服务器失败:{}!'.format(self._pt_pin, e.args))

    async def get_user_info(self, session):
        """
        获取用户信息
        """
        println('{}, 正在获取用户信息!'.format(self._pt_pin))
        url = 'https://m.jingxi.com/jxbfd/user/QueryUserInfo?strZone=jxbfd&bizCode=jxbfd&source=jxbfd&dwEnv=7&_cfd_t' \
              '={}&ptag=7155.9.47&ddwTaskId=&strShareId=&strMarkList=guider_step%2Ccollect_coin_auth' \
              '%2Cguider_medal%2Cguider_over_flag%2Cbuild_food_full%2Cbuild_sea_full%2Cbuild_shop_full' \
              '%2Cbuild_fun_full%2Cmedal_guider_show%2Cguide_guider_show%2Cguide_receive_vistor&_stk=_cfd_t%2CbizCode' \
              '%2CddwTaskId%2CdwEnv%2Cptag%2Csource%2CstrMarkList%2CstrShareId%2CstrZone&_ste=1&h5st' \
              '=20210712211304447%3B3749788196288162%3B10032%3Btk01wb4c61c70a8nMWlTak9Lbk9BuFmz5tA0ShI2vta9gBt8C' \
              '%2FesQ%2F4lluUo%2FG2z3TabYeJFdDr3wrSvtpdn4p44qNq%2F' \
              '%3B95a264579ccce82f781d3edbaa15db700ff98c785fd8bf95bec411563c5ba772&_={}' \
              '&sceneval=2&g_login_type=1&callback=jsonpCBKA&g_ty=ls'.format(get_timestamp(), get_timestamp())
        data = await self.request(session, url)
        return data

    async def get_share_code(self):
        """
        获取助力码
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            data = await self.get_user_info(session)
            if 'strMyShareId' not in data:
                return
            code = data['strMyShareId']
            println('{}, 助力码:{}'.format(self._pt_pin, code))
            return code

    async def run(self):
        """
        程序入口
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            data = await self.get_user_info(session)
            if not data:
                println('{}, 无法获取数据, 退出!'.format(self._pt_pin))


def start(pt_pin, pt_key, name='京喜财富岛'):
    """
    """
    try:
        app = JxCfd(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())

