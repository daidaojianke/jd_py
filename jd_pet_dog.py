#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 9:29 上午
# @File    : jd_pet_dog.py
# @Project : jd_scripts
# @Desc    : 京东APP->我的->宠汪汪
import asyncio
import json
import re
import os
import aiohttp

import base64
import numpy as np
import cv2
import random
from pyppeteer import launcher

launcher.DEFAULT_ARGS.remove("--enable-automation")
from utils.console import println
from PIL import Image, ImageChops
from pyppeteer import launch
from urllib.parse import unquote, quote
from config import USER_AGENT, IMAGES_DIR
from utils.image import save_img, detect_displacement


class JdPetDog:
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
            'dumpio': True,
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
                '--disable-extensions',
                '--hide-scrollbars',
                '--disable-bundled-ppapi-flash',
                '--disable-setuid-sandbox',
                '--disable-xss-auditor',
                '--ignore-certificate-errors',
            ]
        })
        return browser

    async def open_page(self, browser):
        """
        打开页面
        :return:
        """
        context = await browser.createIncognitoBrowserContext()
        pages = await context.pages()
        if len(pages) > 0:
            page = pages[0]
        else:
            page = await browser.newPage()

        await page.setUserAgent(USER_AGENT)  # 设置USER-AGENT

        await page.setViewport({
            'width': 375,
            'height': 712,
            'isMobile': True
        })

        await page.setCookie(*self._cookies)  # 设置cookies

        await page.goto(self.url)  # 打开活动页面

        return page

    async def validate(self):
        """
        :return:
        """
        browser = await self.open_browser()
        page = await self.open_page(browser)

        bg_img_selector = '#man-machine-box > div > div.JDJRV-img-panel.JDJRV-embed > div.JDJRV-img-wrap > ' \
                          'div.JDJRV-bigimg > img'

        slider_img_selector = '#man-machine-box > div > div.JDJRV-img-panel.JDJRV-embed > div.JDJRV-img-wrap > ' \
                              'div.JDJRV-smallimg > img'

        println('等待加载拼图验证背景图片...')
        while not await page.querySelector(bg_img_selector):
            await asyncio.sleep(1)

        bg_img_ele = await page.querySelector(bg_img_selector)

        println('等待加载拼图验证滑块图片...')
        while not await page.querySelector(slider_img_selector):
            await asyncio.sleep(1)
        slider_img_ele = await page.querySelector(slider_img_selector)

        bg_img_content = await (await bg_img_ele.getProperty('src')).jsonValue()
        slider_img_content = await (await slider_img_ele.getProperty('src')).jsonValue()

        bg_image_path = os.path.join(IMAGES_DIR, 'jd_pet_dog_bg.png')
        slider_image_path = os.path.join(IMAGES_DIR, 'jd_pet_dog_slider.png')

        println('保存拼图验证背景图片:{}!'.format(bg_image_path))
        save_img(bg_img_content, bg_image_path)

        println('保存拼图验证滑块图片:{}!'.format(slider_image_path))
        save_img(slider_img_content, slider_image_path)

        top_left = detect_displacement(slider_image_path, bg_image_path)
        println('滑块偏移量:{}'.format(top_left))

        slider_btn_selector = '#man-machine-box > div > div.JDJRV-slide-bg > div.JDJRV-slide-inner.JDJRV-slide-btn'
        # ele = await page.querySelector(slider_btn_selector)
        box = await slider_img_ele.boundingBox()
        println('开启拖动滑块...')
        await page.hover(slider_btn_selector)
        await page.mouse.down()
        await page.mouse.move(top_left, box['y'], {'delay': random.randint(1000, 2000), 'steps': 3})
        await asyncio.sleep(5)
        await page.mouse.up()
        # await self.validate()

    async def run(self):
        cookies = await self.validate()
        print(cookies)


if __name__ == '__main__':
    from config import JD_COOKIES

    app = JdPetDog(*JD_COOKIES[0].values())
    asyncio.run(app.run())
