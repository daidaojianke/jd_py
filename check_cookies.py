#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 2:17 下午
# @File    : check_cookies.py
# @Project : jd_scripts
# @Desc    : 检查cookies是否过期, 过期则发送通知
import asyncio
import aiohttp
import json
from urllib.parse import unquote
from config import JD_COOKIES
from utils.console import println
from utils.notify import notify


async def check_cookies():
    """
    检查配置中的cookies是否已过期, 过期则发送通知
    :return:
    """
    println('开始检查cookies状态, 共{}个!'.format(len(JD_COOKIES)))
    url = 'https://api.m.jd.com/client.action?functionId=newUserInfo&clientVersion=10.0.9&client=android&openudid' \
          '=a27b83d3d1dba1cc&uuid=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&st=1626848394828' \
          '&sign=447ffd52c08f0c8cca47ebce71579283&sv=101&body=%7B%22flag%22%3A%22nickname%22%2C%22fromSource%22%3A1' \
          '%2C%22sourceLevel%22%3A1%7D&'
    headers = {
        'user-agent': 'okhttp/3.12.1;jdmall;android;version/10.0.9;build/89099;screen/1080x2293;os/11;network/wifi;'
    }
    for cookies in JD_COOKIES:
        account = unquote(cookies['pt_pin'])
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            try:
                response = await session.post(url=url)
                text = await response.text()
                data = json.loads(text)
                if data['code'] != '0':
                    println('京东账号:{}, cookies已过期, 请重新配置cookies!'.format(account))
                    notify('京东账号:{}, cookies已过期, 请重新配置cookies!'.format(account))
                else:
                    println('京东账号:{}, cookies状态正常!'.format(account))
            except Exception as e:
                println(e.args)

if __name__ == '__main__':
    asyncio.run(check_cookies())