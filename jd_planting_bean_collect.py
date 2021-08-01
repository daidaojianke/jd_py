#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/31 下午9:22
# @Project : jd_scripts
# @File    : jd_planting_bean_collect.py
# @Cron    : 40 */2 * * *
# @Desc    :
import asyncio
import aiohttp

from utils.console import println
from utils.process import process_start
from jd_planting_bean import JdPlantingBean


class JdPlantingBeanCollect(JdPlantingBean):
    """
    种豆得豆收营养夜
    """
    def __init__(self, pt_pin, pt_key):
        super(JdPlantingBeanCollect, self).__init__(pt_pin, pt_key)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            is_success = await self.planting_bean_index(session)
            if not is_success:
                println('{}, 无法获取活动数据!'.format(self._account))
                return
            await self.receive_nutrient(session)
            await self.collect_nutriments(session)


def start(pt_pin, pt_key, name='种豆得豆收营养液'):
    """
    程序入口
    :param name:
    :param pt_pin:
    :param pt_key:
    :return:
    """
    try:
        app = JdPlantingBeanCollect(pt_pin, pt_key)
        asyncio.run(app.run())
        return app.message
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    # from config import JD_COOKIES
    # start(*JD_COOKIES[2].values())
    process_start(start, '种豆得豆收营养液')
