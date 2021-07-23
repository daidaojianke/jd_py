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
from urllib.parse import unquote, urlencode
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
        self._aiohttp_cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._pt_pin = unquote(pt_pin)
        self.browser = None  # 浏览器对象
        self.page = None  # 页面标签对象

    async def validate(self):
        """
        :return:
        """
        if not self.browser:
            self.browser = await open_browser()
        if not self.page:
            self.page = await open_page(self.browser, self.url, USER_AGENT, self._cookies)
        page = self.page
        validator_selector = '#app > div > div > div > div.man-machine > div.man-machine-container'
        validator = await page.querySelector(validator_selector)
        if not validator:
            println('{}, 不需要拼图验证...'.format(self._pt_pin))
            return True
        else:
            box = await validator.boundingBox()
            if not box:
                println('{}, 不需要拼图验证...'.format(self._pt_pin))
                return True

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
            return True
        else:
            box = await validator.boundingBox()
            if not box:
                println('{}, 已完成拼图验证...'.format(self._pt_pin))
                return True
            else:
                println('{}, 无法完成拼图验证...'.format(self._pt_pin))
                return None

    async def request(self, session, path, body=None, method='GET'):
        """
        请求数据
        :param session:
        :param method:
        :param path:
        :param body:
        :return:
        """
        try:
            if not body:
                body = dict()
            body.update({
                'reqSource': 'h5',
                'invokeKey': 'qRKHmL4sna8ZOP9F'
            })
            url = 'https://jdjoy.jd.com/common/{}'.format(path) + '?' + urlencode(body)
            if method == 'GET':
                response = await session.get(url)
            else:
                response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            if not data['errorCode']:
                if 'data' in data:
                    return data['data']
                if 'datas' in data:
                    return data['datas']
                return data

            if data['errorCode'] == 'H0001':  # 需要拼图验证
                is_success = await self.validate()
                if is_success:
                    return await self.request(session, path, body, method)
            return None
        except Exception as e:
            println('{}, 获取服务器数据失败:{}'.format(self._pt_pin, e.args))
            return None

    async def sign_every_day(self, session, task):
        """
        每日签到
        """
        pass

    async def get_task_food(self, session, task):
        """
        领取任务奖励狗粮
        """
        path = 'pet/getFood'
        body = {
            'taskType': task['taskType']
        }
        data = await self.request(session, path, body)
        if not data:
            println('{}, 领取')

    async def follow_shop(self, session, task):
        """
        关注店铺
        """
        path = 'pet/icon/click'
        shop_list = task['followShops']
        for shop in shop_list:
            params = {
                'iconCode': 'follow_shop',
                'linkAddr': shop['shopId']
            }
            data = await self.request(session, path, params)
            if not data:
                println('{}, 关注店铺:{}失败!'.format(self._pt_pin, shop['name']))
            else:
                println('{}, 成功关注店铺:{}!'.format(self._pt_pin, shop['name']))
            await asyncio.sleep(0.1)

    async def follow_good(self, session, task):
        """
        关注商品
        """
        path = 'pet/icon/click'
        good_list = task['followGoodList']

        for good in good_list:
            params = {
                'iconCode': 'follow_good',
                'linkAddr': good['sku']
            }
            data = await self.request(session, path, params)
            if not data:
                println('{}, 关注商品:{}失败!'.format(self._pt_pin, good['skuName']))
            else:
                println('{}, 成功关注商品:{}!'.format(self._pt_pin, good['skuName']))
            await asyncio.sleep(0.1)

    async def follow_channel(self, session, task):
        """
        """
        path = 'pet/icon/click'
        channel_list = task['followChannelList']

        for channel in channel_list:
            params = {
                'iconCode': 'follow_channel',
                'linkAddr': channel['channelId']
            }
            data = await self.request(session, path, params)
            if not data:
                println('{}, 浏览频道:{}失败!'.format(self._pt_pin, channel['channelName']))
            else:
                println('{}, 成功浏览频道:{}!'.format(self._pt_pin, channel['channelName']))
            await asyncio.sleep(0.1)

    async def do_task_list(self, session):
        """
        做任务
        :return:
        """
        path = 'pet/getPetTaskConfig'
        task_list = await self.request(session, path)
        if not task_list:
            println('{}, 获取任务列表失败!'.format(self._pt_pin))
            return

        for task in task_list:
            println(task)
            if task['receiveStatus'] == 'unreceive':
                await self.get_task_food(session, task)
                await asyncio.sleep(1)

            if task['taskType'] == 'SignEveryDay':
                await self.sign_every_day(session, task)

            elif task['taskType'] == 'FollowShop':
                await self.follow_shop(session, task)

            elif task['taskType'] == 'FollowGood':
                await self.follow_good(session, task)

            elif task['taskType'] == 'FollowChannel':
                await self.follow_channel(session, task)


class JdPetDog(JdPetDogBase):
    """
    宠汪汪
    """
    async def run(self):
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._aiohttp_cookies) as session:
            await self.do_task_list(session)

        if self.browser:
            await self.browser.close()


if __name__ == '__main__':
    from config import JD_COOKIES
    app = JdPetDog(*JD_COOKIES[0].values())
    asyncio.run(app.run())
