#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/9 2:19 下午
# @File    : update_share_code.py
# @Project : jd_scripts
# @Desc    : 获取助力码, 并更新到配置文件中
import asyncio
import yaml
import copy

from utils.console import println
from config import JD_COOKIES, CONF_PATH
from update_config import update_config


from jd_planting_bean import JdPlantingBean
from jd_cash import JdCash
from jd_factory import JdFactory
from jd_cute_pet import JdCutePet
from jd_farm import JdFarm
from jr_money_tree import JrMoneyTree


class UpdateShareCode:
    """
    更新助力码
    """
    @staticmethod
    async def get_share_code(cls, name):
        """
        获取助力码
        :param cls:
        :param name:
        :return:
        """
        println('\n正在获取《{}》助力码, 共:{}个账号...'.format(name, len(JD_COOKIES)))
        code_map = {}
        for i in range(len(JD_COOKIES)):
            cookies = JD_COOKIES[i]
            obj = cls(*cookies.values())
            share_code = await obj.get_share_code()
            if not share_code:
                continue
            code_map[i] = share_code
        sorted(code_map.items(), key=lambda kv: (kv[1], kv[0]))
        code_list = list(code_map.values())
        println('获取《{}》助力码完成...\n'.format(name))
        return code_list

    @classmethod
    def read_config(cls):
        # 加载配置文件
        with open(CONF_PATH, 'r', encoding='utf-8-sig') as f:
            cfg = yaml.safe_load(f)
            return cfg

    @classmethod
    async def run(cls):
        println('#############自动获取助力码##############')
        code_func_map = {
            'jd_planting_bean_code': {
                'cls': JdPlantingBean,
                'name': '种豆得豆',
            },
            'jd_cash_code': {
                'cls': JdCash,
                'name': '签到领现金'
            },
            'jd_cute_pet_code': {
                'cls': JdCutePet,
                'name': '东东萌宠',
            },
            'jd_factory_code': {
                'cls': JdFactory,
                'name': '东东工厂'
            },
            'jd_farm_code': {
                'cls': JdFarm,
                'name': '东东农场',
            },
            'jr_money_tree_code': {
                'cls': JrMoneyTree,
                'name': '金果摇钱树',
            }

        }
        cfg = cls.read_config()

        for key, val in code_func_map.items():
            code_list = await cls.get_share_code(val['cls'], val['name'])
            cfg[key] = list(set([i for i in (cfg.get(key, []) + code_list) if i]))

        println('助力获取完成, 准备写入配置文件: {}中...'.format(CONF_PATH))
        update_config(cfg, copy.copy(cfg))
        println('成功更新助力码到配置文件:{}中...'.format(CONF_PATH))


if __name__ == '__main__':
    app = UpdateShareCode()
    asyncio.run(app.run())


