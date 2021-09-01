#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/30 4:59 下午
# @File    : cookie.py
# @Project : jd_scripts
# @Desc    :
import json

import aiohttp
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def async_check_cookie(cookies):
    """
    检测cookies是否过期
    :return:
    """
    try:
        url = 'https://api.m.jd.com/client.action?functionId=newUserInfo&clientVersion=10.0.9&client=android&openudid' \
              '=a27b83d3d1dba1cc&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&st' \
              '=1626848394828&sign=447ffd52c08f0c8cca47ebce71579283&sv=101&body=%7B%22flag%22%3A%22nickname%22%2C' \
              '%22fromSource%22%3A1%2C%22sourceLevel%22%3A1%7D&'
        headers = {
            'user-agent': 'okhttp/3.12.1;jdmall;android;version/10.0.9;build/89099;screen/1080x2293;os/11;network/wifi;'
        }
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            response = await session.post(url=url, headers=headers)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != '0':
                return False
            else:
                return True
    except Exception as e:
        print(e.args)
        return False


def sync_check_cookie(cookies):
    """
    检测cookies是否过期
    :param cookies:
    :return:
    """
    try:
        url = 'https://api.m.jd.com/client.action?functionId=newUserInfo&clientVersion=10.0.9&client=android&openudid' \
              '=a27b83d3d1dba1cc&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&st' \
              '=1626848394828&sign=447ffd52c08f0c8cca47ebce71579283&sv=101&body=%7B%22flag%22%3A%22nickname%22%2C' \
              '%22fromSource%22%3A1%2C%22sourceLevel%22%3A1%7D&'
        headers = {
            'user-agent': 'okhttp/3.12.1;jdmall;android;version/10.0.9;build/89099;screen/1080x2293;os/11;network/wifi;'
        }
        response = requests.post(url=url, headers=headers, cookies=cookies, verify=False)
        data = response.json()
        if data['code'] != '0':
            return False
        else:
            return True
    except Exception as e:
        print(e.args)
        return False

