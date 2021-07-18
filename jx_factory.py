#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 1:25 下午
# @File    : jx_factory.py
# @Project : jd_scripts
# @Desc    : 京喜App->惊喜工厂
import time
import hmac
import hashlib
import json
import aiohttp
import random
import asyncio
from datetime import datetime
import re
from furl import furl
from urllib.parse import unquote, urlencode, quote
from utils.console import println


def sha512(key, value):
    """
    sha512加密
    """
    obj = hmac.new(key.encode(), value.encode(), hashlib.sha512)
    return obj.hexdigest()


def sha256(key, value):
    """
    sha256加密
    """
    obj = hmac.new(key.encode(), value.encode(), hashlib.sha256)
    return obj.hexdigest()


def generate_fp():
    """
    生成获取签名算法参数的请求参数
    """
    e = "0123456789"
    a = 13
    i = ''
    while a > 0:
        i += e[int(random.random() * len(e)) | 0]
        a -= 1
    i += str(int(time.time()*100))
    return i[0:16]


class JxFactory:
    headers = {
        'referer': 'https://st.jingxi.com/',
        'user-agent': 'jdpingou;android;4.11.0;11;a27b83d3d1dba1cc;network/wifi;model/RMX2121;appBuild/17304;partner/oppo01;;session/136;aid/a27b83d3d1dba1cc;oaid/;pap/JA2019_3111789;brand/realme;eu/1623732683334633;fv/4613462616133636;Mozilla/5.0 (Linux; Android 11; RMX2121 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.120 Mobile Safari/537.36'
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
        self._inserted_electric = 0   # 已投入电量
        self._need_electric = 0  # 总共需要的电量
        self._production_id = 0  # 商品ID
        self._production_stage_progress = ''  # 生产进度
        self._phone_id = ''  # 设备ID
        self._pin = ''  # 账号ID

        self._token = None  # 签名的TOKEN
        self._algo = None  # 签名算法
        self._fp = generate_fp()  # 签名算法参数
        self._appid = '10001'  #
        self._random = None  #

    async def request(self, session, path, params, method='GET'):
        """
        """
        try:
            default_params = {
                '_time': int(time.time() * 1000),
                'g_ty': 'ls',
                'callback': 'jsonp',
                'sceneval': '2',
                'g_login_type': '1',
                '_': int(time.time() * 1000),
                '_ste': '1',
                'zone': 'dream_factory'
            }
            params.update(default_params)
            url = self._host + path + '?' + urlencode(params)
            h5st = await self.encrypt('', url)
            url += '&h5st={}'.format(h5st)
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

    async def get_encrypt(self):
        """
        获取签名算法
        """
        url = 'https://cactus.jd.com/request_algo?g_ty=ajax'
        headers = {
            'Authority': 'cactus.jd.com',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Content-Type': 'application/json',
            'Origin': 'https://st.jingxi.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://st.jingxi.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7'
        }
        body = {
            "version": "1.0",
            "fp": self._fp,
            "appId": self._appid,
            "timestamp": int(time.time()*1000),
            "platform": "web",
            "expandParams": ""
        }

        try:
            async with aiohttp.ClientSession(cookies=self._cookies, headers=headers) as session:
                response = await session.post(url=url, data=json.dumps(body))
                text = await response.text()
                data = json.loads(text)
                if data['status'] == 200:
                    self._token = data['data']['result']['tk']
                    self._algo = data['data']['result']['algo']
                    self._random = re.search("random='(.*)';", self._algo).group(1)
                    println('{}, 签名Token:{}!'.format(self._pt_pin, self._token))
                else:
                    println('{}, 获取签名算法失败!'.format(self._pt_pin))

        except Exception as e:
            println('{}, 获取签名算法失败, {}!'.format(self._pt_pin, e.args))

    async def encrypt(self, stk='', url=''):
        """
        获取签名
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[0:17]
        if not stk:
            url = furl(url)
            stk = url.args.get('_stk', '')
        s = '{}{}{}{}{}'.format(self._token, self._fp, timestamp, self._appid, self._random)
        hash1 = sha512(s, self._token)
        tmp = []
        tmp_url = furl(url)
        for key in stk.split(','):
            if key == '':
                continue
            tmp_s = '{}:{}'.format(key, tmp_url.args.get(key, ''))
            tmp.append(tmp_s)
        st = '&'.join(tmp)
        hash2 = sha256(st, hash1)
        return quote(';'.join([str(timestamp), str(self._fp), self._appid, self._token, hash2]))

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
            'source': ''
        }
        data = await self.request(session, path, params)
        if data['ret'] != 0:
            println('{}, 获取用户数据失败, {}!'.format(self._pt_pin, data['msg']))
            return None
        return data

    async def get_user_electricity(self, session):
        """
        查询用户电量
        """
        path = 'dreamfactory/generator/QueryCurrentElectricityQuantity'
        body = {
            'factoryid': self._factory_id,
            '_stk': '_time,factoryid,zone',
        }
        data = await self.request(session, path, body)
        println(data)

    async def init(self, session):
        """
        初始化
        """
        user_info = await self.get_user_info(session)
        if not user_info:
            return False
        if 'factoryList' not in user_info:
            println('{}, 未开启活动!'.format(self._pt_pin))
            return False
        self._factory_id = user_info['factoryList'][0]['factoryId']

        if 'productionList' not in user_info:
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
            await self.get_user_electricity(session)

def start(pt_pin, pt_key):
    """
    """
    app = JxFactory(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    println(generate_fp())
    from config import JD_COOKIES
    start(*JD_COOKIES[0].values())

