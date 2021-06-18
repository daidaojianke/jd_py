#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/18 6:33 下午
# @File    : jd_big_winner.py
# @Project : jd_scripts
# @Desc    : 省钱大赢家翻翻乐
import asyncio
import json
from urllib.parse import quote
import aiohttp


from config import USER_AGENT


class BigWinner:
    link_id = 'DA4SkG7NXupA9sksI00L0g'
    ffl_link_id = 'YhCkrVusBVa_O2K-7xE6hA'
    headers = {
        'Host': 'api.m.jd.com',
        'Origin': 'https://openredpacket-jdlite.jd.com',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': USER_AGENT,
        'Referer': 'https://618redpacket.jd.com/withdraw?activityId={}&channel'
                   '=wjicon&lng=&lat=&sid=&un_area='.format(link_id),
        'Accept-Language': 'zh-cn',
    }

    def __init__(self, pt_pin='', pt_key=''):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._pt_pin = pt_pin
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        print(self._cookies)

    async def into_home_page(self, session):
        """
        :return:
        """
        body = {
            'linkId': self.ffl_link_id
        }
        url = 'https://api.m.jd.com/?functionId=gambleHomePage&body={}' \
              '&appid=activities_platform&clientVersion=3.5.0'.format(quote(json.dumps(body)))
        print(url)
        response = await session.get(url=url)
        text = await response.json()
        print(text)

    async def run(self):
        """
        :return:
        """

        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            await self.into_home_page(session)


if __name__ == '__main__':
    print(USER_AGENT)
    app = BigWinner(pt_pin='asfa', pt_key='sfafs')
    asyncio.run(app.run())