#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/26 11:18 上午
# @File    : jd_cool_summer.py
# @Project : jd_scripts
# @Cron    : 8 8 * * *
# @Desc    : 清凉一夏

import asyncio
import json
import re
import time

import aiohttp
from urllib3 import disable_warnings
from requests import Session
from urllib.parse import urlencode
from config import USER_AGENT
from utils.jd_init import jd_init
from utils.logger import logger
from utils.process import process_start
from utils.console import println

disable_warnings()


@jd_init
class JdCoolSummer:
    headers = {
        'USER-AGENT': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded;utf-8',
    }

    token = None
    active_id = None
    task_list = None

    @logger.catch
    async def get_activity_info(self):
        """
        :return:
        """
        try:
            session = Session()
            session.headers.update(self.headers)
            session.cookies.update(self.cookies)
            println('{}, 正在获取活动数据!'.format(self.account))
            url = 'https://api.m.jd.com/client.action?functionId=genToken&clientVersion=10.1.2&build=89739&client=android' \
                  '&partner=jingdong&openudid=a27b83d3d1dba1cc&lang=zh_CN&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc' \
                  '&networkType=wifi&st=1629948091540&sign=eafa3c929da816504f1c19377d28b8fd&sv=122&body=%7B%22action%22' \
                  '%3A%22to%22%2C%22to%22%3A%22https%253A%252F%252Fanmp.jd.com%252FbabelDiy%252FZeus' \
                  '%252F3pG9h6Buegznv8rhVMzMR753pUtY%252Findex.html%253FinnerIndex%253D1%2526tttparams' \
                  '%253DaPn8sCeyJnTGF0IjoiMjMuMDE1NDExIiwiZ0xuZyI6IjExMy4zODgwOTIifQ6%25253D%25253D%2526lng%253D113' \
                  '.383417%2526lat%253D23.103291%2526un_area%253D19_1601_36953_50397%22%7D'
            response = session.get(url, verify=False)
            text = response.text
            token_key = json.loads(text)['tokenKey']
            url = 'https://un.m.jd.com/cgi-bin/app/appjmp?tokenKey={}' \
                  '&to=https%3A%2F%2Fanmp.jd.com%2FbabelDiy%2FZeus%2F3pG9h6Buegznv8rhVMzMR753pUtY%2Findex.html' \
                  '%3FinnerIndex%3D1%26tttparams%3D1aXBwdeyJnTGF0IjoiMjMuMDE1NDExIiwiZ0xuZyI6IjExMy4zODgwOTIifQ6%253D' \
                  '%253D%26lng%3D113.383417%26lat%3D23.103291%26un_area%3D19_1601_36953_50397&lbs=%7B%22lat%22%3A%2223' \
                  '.103291%22%2C%22lng%22%3A%22113.383417%22%2C%22provinceId%22%3A%2219%22%2C%22cityId%22%3A%221601%22%2C' \
                  '%22districtId%22%3A%223634%22%2C%22provinceName%22%3A%22%E5%B9%BF%E4%B8%9C%22%2C%22cityName%22%3A%22' \
                  '%E5%B9%BF%E5%B7%9E%E5%B8%82%22%2C%22districtName%22%3A%22%E6%B5%B7%E7%8F%A0%E5%8C%BA%22%7D'. \
                format(token_key)
            response = session.get(url, verify=False)
            text = response.text
            temp = re.search('var snsConfig =(.*)var SharePlatforms', text, re.S).group(1)
            data = json.loads(temp)
            self.token = data.get('actToken')
            self.active_id = data.get('activeId')
            self.task_list = data['config']['tasks']

            return True
        except Exception as e:
            println('{}, 获取活动数据失败, {}'.format(self.account, e.args))
            return False

    async def request(self, session, path='', body=None, method='GET'):
        """
        :param method:
        :param body:
        :param path:
        :param session:
        :return:
        """
        try:
            if not body:
                body = dict()
            params = {
                'sceneval': 2,
                'activeid': self.active_id,
                'token': self.token,
                't': int(time.time() * 1000),
                'callback': '',
                '_': int(time.time() * 1000)
            }
            params.update(body)
            session.headers.add('referer', 'https://anmp.jd.com/babelDiy/Zeus/3pG9h6Buegznv8rhVMzMR753pUtY/index.html')
            url = 'https://wq.jd.com/{}?'.format(path) + urlencode(params)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)
            text = await response.text()
            text = re.search('{.*}', text).group()
            data = json.loads(text)
            return data
        except Exception as e:
            println('{}, 请求数据失败, {}'.format(self.account, e.args))
            return None

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(cookies=self.cookies, headers=self.headers) as session:
            success = await self.get_activity_info()

            if not success:
                println('{}, 获取活动数据失败, 退出程序!'.format(self.account))
                return

            login_data = await self.request(session, 'mlogin/wxv3/LoginCheckJsonp', {
                'r': '0.192626983227462122',
                'callback': ''
            })
            if login_data.get('iRet') != '0':
                println('{}, 登录失败, 退出程序!'.format(self.account))
                return

            for task in self.task_list:
                res = await self.request(session, 'activet2/piggybank/completeTask', {
                    'task_bless': '10',
                    'taskid': task['_id'],
                    'callback': ''
                })

                if res.get('errcode') == 0:
                    println('{}, 完成任务:{}'.format(self.account, task['_id']))
                elif res.get('errcode') == 9005:
                    println('{}, 需要手动进入活动页面:https://anmp.jd.com/babelDiy/Zeus/3pG9h6Buegznv8rhVMzMR753pUtY/index.html'.format(self.account))
                    break
                await asyncio.sleep(1)

            while True:
                res = await self.request(session, '/activet2/piggybank/draw')
                if res.get('errcode') == 0:
                    println('{}, 抽奖成功!'.format(self.account))
                else:
                    println('{}, 抽奖失败!'.format(self.account))
                    break
                await asyncio.sleep(1)


if __name__ == '__main__':
    process_start(JdCoolSummer, '清凉一夏')
