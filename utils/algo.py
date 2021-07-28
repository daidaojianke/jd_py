#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 4:50 下午
# @File    : algo.py
# @Project : jd_scripts
# @Desc    : 加密算法
import hashlib
import aiohttp
import hmac
import json
import random
import time
from furl import furl
import re
from utils.console import println


def hmacSha256(key, value):
    """
    sha256加密
    """
    obj = hmac.new(value.encode(), key.encode(), hashlib.sha256)
    return obj.hexdigest()


def hmacSha512(key, value):
    """
    :param key:
    :param value:
    :return:
    """
    obj = hmac.new(value.encode(), key.encode(), hashlib.sha512)
    return obj.hexdigest()


def md5(value):
    """
    :param value:
    :return:
    """
    obj = hashlib.md5()
    obj.update(value.encode())
    return obj.hexdigest()


def sha512(value):
    """
    :param value:
    :return:
    """
    obj = hashlib.sha512()
    obj.update(value.encode())
    return obj.hexdigest()


def sha256(value):
    """
    :param value:
    :return:
    """
    obj = hashlib.sha256()
    obj.update(value.encode())
    return obj.hexdigest()


def hmacMD5(key, value):
    """
    :param key:
    :param value:
    :return:
    """
    obj = hmac.new(value.encode(), key.encode('utf-8'), hashlib.md5)
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


class JxSignAlgoMixin:
    """
    京喜APP签名算法混入类
    """
    algo_map = {
        'md5': md5,
        'hmacmd5': hmacMD5,
        'sha256': sha256,
        'hmacsha256': hmacSha256,
        'sha512': sha512,
        'hmacsha512': hmacSha512,
    }

    async def get_encrypt(self):
        """
        获取签名算法
        """
        if not hasattr(self, '_fp'):
            self._fp = generate_fp()

        if not hasattr(self, '_appid'):
            self._appid = '10001'

        url = 'https://cactus.jd.com/request_algo?g_ty=ajax'
        headers = {
            'Authority': 'cactus.jd.com',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
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
                    self._random = re.search("random='(.*)';", data['data']['result']['algo']).group(1)
                    algo = re.search(r'algo\.(.*)\(', data['data']['result']['algo']).group(1)

                    if algo.lower() in self.algo_map:
                        self._algo = self.algo_map[algo.lower()]
                    else:
                        algo = 'hmacsha512'
                        self._algo = self.algo_map[algo]
                        self._random = '5gkjB6SpmC9s'
                        self._token = 'tk01wcdf61cb3a8nYUtHcmhSUFFCfddDPRvKvYaMjHkxo6Aj7dhzO+GXGFa9nPXfcgT' \
                                      '+mULoF1b1YIS1ghvSlbwhE0Xc'
                    println('{}, Token:{}!\n签名算法:{}!'.format(self._pt_pin, self._token, algo))
                else:
                    println('{}, 获取签名算法失败!'.format(self._pt_pin))

        except Exception as e:
            println('{}, 获取签名算法失败, {}!'.format(self._pt_pin, e.args))

    async def encrypt(self, timestamp=None, url='',  stk=''):
        """
        获取签名
        """
        timestamp = timestamp.strftime('%Y%m%d%H%M%S%f')[0:17]
        if not stk:
            url = furl(url)
            stk = url.args.get('_stk', '')

        s = '{}{}{}{}{}'.format(self._token, self._fp, timestamp, self._appid, self._random)
        try:
            hash1 = self._algo(s, self._token)
        except Exception as e:
            hash1 = self._algo(s)
        tmp = []
        tmp_url = furl(url)
        for key in stk.split(','):
            if key == '':
                continue
            tmp_s = '{}:{}'.format(key, tmp_url.args.get(key, ''))
            tmp.append(tmp_s)
        st = '&'.join(tmp)
        hash2 = hmacSha256(st, hash1)
        return ';'.join([str(timestamp), str(self._fp), self._appid, self._token, hash2])