#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 9:29 上午
# @File    : jd_pet_dog.py
# @Project : jd_scripts
# @Desc    : 京东APP->我的->宠汪汪
import asyncio
import json
import aiohttp
from pyppeteer import launcher

launcher.DEFAULT_ARGS.remove("--enable-automation")

from pyppeteer import launch

from urllib.parse import unquote, quote
from config import USER_AGENT


def hook_request(request):
    """
    :return:
    """
    print(request.url, request.method, request.postData)


def hook_response(*args, **kwargs):
    print(args)
    print(kwargs)


class JdDog:
    """
    宠汪汪, 需要使用浏览器方式进行拼图验证。
    """

    # 活动地址
    url = 'https://h5.m.jd.com/babelDiy/Zeus/2wuqXrZrhygTQzYA7VufBEpj4amH/index.html#/pages/jdDog/jdDog'

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = [
            {
                'domain': '.jd.com',
                'name': 'pt_pin',
                'value': pt_pin,
            },
            {
                'domain': '.jd.com',
                'name': 'pt_key',
                'value': pt_key,
            }
        ]
        self._pt_pin = unquote(pt_pin)

    async def open_browser(self):
        """
        打开浏览器
        :return:
        """
        browser = await launch({
            'headless': False,
            # 'dumpio': True,
            'slowMo': 30,
            'devtools': True,
            'autoClose': False,
            'handleSIGTERM': True,
            'handleSIGINT': True,
            'handleSIGHUP': True,
            'args': [
                '--no-sandbox',
                '--disable-gpu',
                '--disable-infobars',
                '-–window-size=1920,1080',
            ]
        })
        return browser

    async def open_page(self, browser):
        """
        打开页面
        :return:
        """
        pages = await browser.pages()
        if len(pages) > 0:
            page = pages[0]
        else:
            page = await browser.newPage()

        page.on('request', hook_request)
        await page.setUserAgent(USER_AGENT)  # 设置USER-AGENT

        await page.setViewport({
            'width': 375,
            'height': 712,
            'isMobile': True
        })

        await page.setCookie(*self._cookies)  # 设置cookies

        await page.goto(self.url)  # 打开活动页面

        return page

    async def run(self):
        browser = await self.open_browser()
        page = await self.open_page(browser)
        await browser.close()


if __name__ == '__main__':
    from config import JD_COOKIES

    app = JdDog(*JD_COOKIES[0].values())
    asyncio.run(app.run())
