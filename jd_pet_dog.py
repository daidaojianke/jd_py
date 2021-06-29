#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 9:29 上午
# @File    : jd_pet_dog.py
# @Project : jd_scripts
# @Desc    : 京东APP->我的->宠汪汪
import asyncio
import platform
import os
import random
from pyppeteer import launcher

launcher.DEFAULT_ARGS.remove("--enable-automation")
from utils.console import println
from pyppeteer import launch
from urllib.parse import unquote, quote
from config import USER_AGENT, IMAGES_DIR
from utils.image import save_img, detect_displacement


async def open_browser():
    """
    打开浏览器
    :return:
    """
    if platform.system() == 'Linux':
        headless = True
    else:
        headless = False
    browser = await launch({
        'headless': headless,
        'dumpio': True,
        'slowMo': 30,
        # 'devtools': True,
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
            '--use-fake-ui-for-media-stream'
        ]
    })

    return browser


class JdPetDogBase:
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
            'width': 500,
            'height': 845,
            'isMobile': True
        })

        await page.setCookie(*self._cookies)  # 设置cookies

        await page.goto(self.url, timeout=40000)  # 打开活动页面

        return page

    async def validate(self):
        """
        :return:
        """
        browser = await open_browser()
        page = await self.open_page(browser)

        validator_selector = '#app > div > div > div > div.man-machine > div.man-machine-container'
        validator = await page.querySelector(validator_selector)
        if not validator:
            println('不需要拼图验证...')
            return await page.cookies()
        else:
            box = await validator.boundingBox()
            if not box:
                println('不需要拼图验证...')
                return await page.cookies()

        println('需要进行拼图验证...')

        bg_img_selector = '#man-machine-box > div > div.JDJRV-img-panel.JDJRV-embed > div.JDJRV-img-wrap > ' \
                          'div.JDJRV-bigimg > img'

        slider_img_selector = '#man-machine-box > div > div.JDJRV-img-panel.JDJRV-embed > div.JDJRV-img-wrap > ' \
                              'div.JDJRV-smallimg > img'

        for i in range(10):

            println('正在进行第{}次拼图验证...'.format(i))
            println('等待加载拼图验证背景图片...')
            await page.waitForSelector(bg_img_selector)
            # while not await page.querySelector(bg_img_selector):
            #     await asyncio.sleep(1)

            bg_img_ele = await page.querySelector(bg_img_selector)

            println('等待加载拼图验证滑块图片...')
            await page.waitForSelector(slider_img_selector)
            # while not await page.querySelector(slider_img_selector):
            #     await asyncio.sleep(1)
            slider_img_ele = await page.querySelector(slider_img_selector)

            bg_img_content = await (await bg_img_ele.getProperty('src')).jsonValue()
            slider_img_content = await (await slider_img_ele.getProperty('src')).jsonValue()

            bg_image_path = os.path.join(IMAGES_DIR, 'jd_pet_dog_bg.png')
            slider_image_path = os.path.join(IMAGES_DIR, 'jd_pet_dog_slider.png')

            println('保存拼图验证背景图片:{}!'.format(bg_image_path))
            save_img(bg_img_content, bg_image_path)

            println('保存拼图验证滑块图片:{}!'.format(slider_image_path))
            save_img(slider_img_content, slider_image_path)

            offset = detect_displacement(slider_image_path, bg_image_path)
            println('拼图偏移量为:{}'.format(offset))

            slider_btn_selector = '#man-machine-box > div > div.JDJRV-slide-bg > div.JDJRV-slide-inner.JDJRV-slide-btn'
            ele = await page.querySelector(slider_btn_selector)
            box = await ele.boundingBox()
            println('开始拖动拼图滑块...')
            await page.hover(slider_btn_selector)
            await page.mouse.down()

            cur_x = box['x']
            cur_y = box['y']
            first = True
            total_delay = 0
            shake_times = 2  # 左右抖动的最大次数

            while offset > 0:
                if first:
                    # 第一次先随机移动偏移量的%60~80%
                    x = int(random.randint(6, 8) / 10 * offset)
                    first = False
                elif total_delay >= 2000:  # 时间大于2s了， 直接拉满
                    x = offset
                else:  # 随机滑动5~30px
                    x = random.randint(5, 30)

                if x > offset:
                    offset = 0
                    x = offset
                else:
                    offset -= x

                cur_x += x

                delay = random.randint(100, 500)
                steps = random.randint(1, 20)
                total_delay += delay
                println('拼图offset:{}, delay:{}, steps:{}'.format(cur_x, delay, steps))
                await page.mouse.move(cur_x, cur_y,
                                      {'delay': delay, 'steps': steps})

                if shake_times <= 0:
                    continue

                if total_delay >= 2000:
                    continue

                num = random.randint(1, 10)  # 随机选择是否抖动
                if num % 2 == 1:
                    continue

                shake_times -= 1
                px = random.randint(1, 20)  # 随机选择抖动偏移量
                delay = random.randint(100, 500)
                steps = random.randint(1, 20)
                total_delay += delay
                # 往右拉
                cur_x += px
                println('拼图向右滑动:offset:{}, delay:{}, steps:{}'.format(px, delay, steps))
                await page.mouse.move(cur_x, cur_y,
                                      {'delay': delay, 'steps': steps})

                delay = random.randint(100, 500)
                steps = random.randint(1, 20)
                total_delay += delay

                # 往左拉
                cur_x -= px
                println('拼图向左滑动:offset:{}, delay:{}, steps:{}'.format(px, delay, steps))
                await page.mouse.move(cur_x, cur_y,
                                      {'delay': delay, 'steps': steps})
            println('第{}次拼图验证, 耗时:{}s.'.format(i, total_delay / 1000))
            await page.mouse.up()
            await asyncio.sleep(3)
            println('正在获取验证结果, 等待3s...')
            slider_img_ele = await page.querySelector(slider_img_selector)
            if slider_img_ele is None:
                println('第{}次拼图验证, 验证成功!'.format(i))
            else:
                println('第{}次拼图验证, 验证失败, 继续验证!'.format(i))

        validator = await page.querySelector(validator_selector)
        if not validator:
            println('已完成拼图验证...')
            return await page.cookies()
        else:
            box = await validator.boundingBox()
            if not box:
                println('已完成拼图验证...')
                return await page.cookies()
            else:
                println('无法完成拼图验证...')
                return None

    async def get_cookies(self):
        """
        获取拼图验证后的cookies
        :return:
        """
        result_cookies = dict()
        cookies = await self.validate()
        if not cookies:
            return None
        for cookie in cookies:
            result_cookies[cookie['name']] = cookie['value']

        return result_cookies

    async def run(self):
        pass


class JdPetDogTask(JdPetDogBase):
    async def run(self):
        cookies = await self.get_cookies()
        if not cookies:
            println('{}, 获取COOKIES失败, 退出程序...'.format(self._pt_pin))
            return
        println(cookies)


if __name__ == '__main__':
    from config import JD_COOKIES

    app = JdPetDogTask(*JD_COOKIES[0].values())
    asyncio.run(app.run())
