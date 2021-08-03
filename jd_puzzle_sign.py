#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/8/3 下午7:24
# @Project : jd_scripts
# @File    : jd_puzzle_sign.py
# @Cron    :
# @Desc    : 京东拼图签到
import asyncio
from utils.console import println
from utils.wraps import jd_init
from utils.browser import open_browser, open_page
from config import USER_AGENT
from utils.validate import puzzle_validate_decorator


@jd_init
@puzzle_validate_decorator
class JdPuzzleSign:
    """
    京东拼图签到
    """
    browser_cookies = []
    user_agent = 'jdapp;' + USER_AGENT

    async def undies_sign(self, browser):
        """
        京东内衣签到
        :return:
        """
        url = 'https://pro.m.jd.com/mall/active/4PgpL1xqPSW1sVXCJ3xopDbB1f69/index.html#/'
        println('{}, 正在打开京东内衣页面...'.format(self.account))
        page = await open_page(browser, url, self.user_agent, self.browser_cookies)

        sign_button_selector = '#J_babelOptPage > div > div.bab_opt_mod.bab_opt_mod_1_4.module_60978540.customcode' \
                               '.shared > div > div.sign_contain > div.sign_btn'

        await page.waitForSelector(sign_button_selector)

        sign_button_element = await page.querySelector(sign_button_selector)
        sign_button_text = await (await sign_button_element.getProperty("textContent")).jsonValue()
        if sign_button_text.strip() != '立即翻牌':
            println('{}, 京东内衣今日已签到!'.format(self.account))
            return
        println('{}, 立即翻牌！'.format(self.account))
        await sign_button_element.click()
        await asyncio.sleep(1)
        # document.getElementsByClassName('man-machine-container')[0].style.cssText='width:400px;height:299px';
        await self.puzzle_validate(page, (32, 32), (230, 89))

    async def run(self):
        """
        签到入口
        :return:
        """
        self.browser_cookies = [
            {
                'domain': '.jd.com',
                'name': 'pt_pin',
                'value': self.cookies.get('pt_pin'),
            },
            {
                'domain': '.jd.com',
                'name': 'pt_key',
                'value': self.cookies.get('pt_key'),
            }
        ]
        println('{}, 正在打开浏览器...'.format(self.account))
        browser = await open_browser()
        await self.undies_sign(browser)


if __name__ == '__main__':
    from config import JD_COOKIES
    app = JdPuzzleSign(**JD_COOKIES[4])
    asyncio.run(app.run())
