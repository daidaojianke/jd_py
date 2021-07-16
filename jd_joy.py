#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/25 9:29 上午
# @File    : jd_joy.py
# @Project : jd_scripts
# @Desc    : 京东APP->我的->宠汪汪
import asyncio
import json
import os
import random
import aiohttp
from utils.console import println
from urllib.parse import unquote
from config import USER_AGENT, IMAGES_DIR
from utils.image import save_img, detect_displacement
from utils.browser import open_page, open_browser


class JdPetDogBase:
    """
    宠汪汪, 需要使用浏览器方式进行拼图验证。
    """
    # 活动地址
    url = 'https://h5.m.jd.com/babelDiy/Zeus/2wuqXrZrhygTQzYA7VufBEpj4amH/index.html#/pages/jdDog/jdDog'

    headers = {
        "Accept": "application/json,text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Referer": "https://h5.m.jd.com/babelDiy/Zeus/2wuqXrZrhygTQzYA7VufBEpj4amH/index.html",
        "User-Agent":  USER_AGENT
    }

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

    async def validate(self):
        """
        :return:
        """
        browser = await open_browser()
        page = await open_page(browser, self.url, USER_AGENT, self._cookies)

        validator_selector = '#app > div > div > div > div.man-machine > div.man-machine-container'
        validator = await page.querySelector(validator_selector)
        if not validator:
            println('{}, 不需要拼图验证...'.format(self._pt_pin))
            return await page.cookies()
        else:
            box = await validator.boundingBox()
            if not box:
                println('{}, 不需要拼图验证...'.format(self._pt_pin))
                return await page.cookies()

        println('{}, 需要进行拼图验证...'.format(self._pt_pin))

        bg_img_selector = '#man-machine-box > div > div.JDJRV-img-panel.JDJRV-embed > div.JDJRV-img-wrap > ' \
                          'div.JDJRV-bigimg > img'

        slider_img_selector = '#man-machine-box > div > div.JDJRV-img-panel.JDJRV-embed > div.JDJRV-img-wrap > ' \
                              'div.JDJRV-smallimg > img'

        for i in range(10):

            println('{}, 正在进行第{}次拼图验证...'.format(self._pt_pin, i+1))
            println('{}, 等待加载拼图验证背景图片...'.format(self._pt_pin))
            await page.waitForSelector(bg_img_selector)

            bg_img_ele = await page.querySelector(bg_img_selector)

            println('{}, 等待加载拼图验证滑块图片...'.format(self._pt_pin))
            await page.waitForSelector(slider_img_selector)
            slider_img_ele = await page.querySelector(slider_img_selector)

            bg_img_content = await (await bg_img_ele.getProperty('src')).jsonValue()
            slider_img_content = await (await slider_img_ele.getProperty('src')).jsonValue()

            bg_image_path = os.path.join(IMAGES_DIR, 'jd_pet_dog_bg_{}.png'.format(self._pt_pin))
            slider_image_path = os.path.join(IMAGES_DIR, 'jd_pet_dog_slider_{}.png'.format(self._pt_pin))

            println('{}, 保存拼图验证背景图片:{}!'.format(self._pt_pin, bg_image_path))
            save_img(bg_img_content, bg_image_path)

            println('{}, 保存拼图验证滑块图片:{}!'.format(self._pt_pin, slider_image_path))
            save_img(slider_img_content, slider_image_path)

            offset = detect_displacement(slider_image_path, bg_image_path)
            println('{}. 拼图偏移量为:{}'.format(self._pt_pin, offset))

            slider_btn_selector = '#man-machine-box > div > div.JDJRV-slide-bg > div.JDJRV-slide-inner.JDJRV-slide-btn'
            ele = await page.querySelector(slider_btn_selector)
            box = await ele.boundingBox()
            println('{}, 开始拖动拼图滑块...'.format(self._pt_pin))
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
                println('{}, 拼图offset:{}, delay:{}, steps:{}'.format(self._pt_pin, cur_x, delay, steps))
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
                println('{}, 拼图向右滑动:offset:{}, delay:{}, steps:{}'.format(self._pt_pin, px, delay, steps))
                await page.mouse.move(cur_x, cur_y,
                                      {'delay': delay, 'steps': steps})

                delay = random.randint(100, 500)
                steps = random.randint(1, 20)
                total_delay += delay

                # 往左拉
                cur_x -= px
                println('{}, 拼图向左滑动:offset:{}, delay:{}, steps:{}'.format(self._pt_pin, px, delay, steps))
                await page.mouse.move(cur_x, cur_y,
                                      {'delay': delay, 'steps': steps})
            println('{}, 第{}次拼图验证, 耗时:{}s.'.format(self._pt_pin, i+1, total_delay / 1000))
            await page.mouse.up()
            await asyncio.sleep(3)
            println('{}, 正在获取验证结果, 等待3s...'.format(self._pt_pin))
            slider_img_ele = await page.querySelector(slider_img_selector)
            if slider_img_ele is None:
                println('{}, 第{}次拼图验证, 验证成功!'.format(self._pt_pin, i+1))
                break
            else:
                println('{}, 第{}次拼图验证, 验证失败, 继续验证!'.format(self._pt_pin, i+1))

        validator = await page.querySelector(validator_selector)
        if not validator:
            println('{}, 已完成拼图验证...'.format(self._pt_pin))
            return await page.cookies()
        else:
            box = await validator.boundingBox()
            if not box:
                println('{}, 已完成拼图验证...'.format(self._pt_pin))
                return await page.cookies()
            else:
                println('{}, 无法完成拼图验证...'.format(self._pt_pin))
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

    async def get(self, session, url):
        """
        :param session:
        :param url:
        :param body:
        :return:
        """
        try:
            response = await session.get(url)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            println('{}, 获取服务器数据失败:{}'.format(self._pt_pin, e.args))

    async def get_task_list(self, session):
        """
        获取任务列表
        :return:
        """
        url = 'https://jdjoy.jd.com/common/pet/getPetTaskConfig?reqSource=h5&invokeKey=NRp8OPxZMFXmGkaE'
        data = await self.get(session, url)
        println(data)


class JdPetDogTask(JdPetDogBase):
    """
    宠汪汪任务
    """
    async def run(self):
        cookies = await self.get_cookies()
        if not cookies:
            println('{}, 获取COOKIES失败, 退出程序...'.format(self._pt_pin))
            return
        async with aiohttp.ClientSession(headers=self.headers, cookies=cookies) as session:
            await self.get_task_list(session)


if __name__ == '__main__':
    from config import JD_COOKIES
    app = JdPetDogTask(*JD_COOKIES[0].values())
    asyncio.run(app.run())
