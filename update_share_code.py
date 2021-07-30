#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/9 2:19 下午
# @File    : update_share_code.py
# @Project : jd_scripts
# @Desc    : 获取助力码, 并更新到配置文件中
import asyncio
import copy

from utils.console import println
from jd_planting_bean import JdPlantingBean
from jd_cash import JdCash
from jd_factory import JdFactory
from jd_cute_pet import JdCutePet
from jd_farm import JdFarm
from jr_money_tree import JrMoneyTree
from jd_wishing_pool import JdWishingPool
# from jd_burning_summer import JdBurningSummer
from jd_smash_golden_egg import JdSmashGoldenEgg
from dj_fruit import DjFruit
from jd_grab_bean import JdGrabBean
import shutil
import yaml
from config import CONF_PATH, EXAMPLE_CONFIG_PATH, BAK_CONFIG_PATH, JD_COOKIES


def update_config(old_cfg=None, new_cfg=None):
    """
    更新配置文件
    :return:
    """
    comment_map = {
        'debug': '# 控制输出, true打开输出, false关闭输出',
        'process_num': '# 开启多个进程',
        'jd_cookies': '# 京东账号Cookies, 一行一个, 填写顺序影响助力码顺序!',
        'jd_planting_bean_code': '# 种豆得豆互助码, 一行一个, 按填写顺序助力!',
        'jd_cute_pet_code': '# 东东萌宠互助码, 一行一个, 按填写顺序助力!',
        'jd_factory_code': '# 东东工厂互助码, 一行一个, 按填写顺序助力!',
        'jd_farm_code': '# 东东农场互助码, 一行一个, 按填写顺序助力!',
        'jr_money_tree_code': '# 金果摇钱树互助码, 一行一个, 按填写顺序助力!',
        'jd_sgmh_code': '# 闪购盲盒互助码, 一行一个, 按填写顺序助力!',
        'jx_factory_share_code': '# 京喜工厂互助码， 一行一个, 按填写顺序助力!',
        'jx_farm_code': '# 京喜农场互助码, 一行一个, 按填写顺序助力!',
        'jd_cash_code': '# 京东签到领现金助力码, 一行一个, 按填写顺序助力!',
        'notify': '# TG消息通知配置',
        'user_agent': '# 请求头, 需要替换自行抓包, 否则不填使用默认即可',
        'tg_bot_token': '# TG 机器人Token',
        'tg_user_id': '# TG用户ID',
        'jd_farm_bean_card': '# 是否使用水滴换豆卡, 100水滴换20京豆',
        'jd_farm_retain_water': '# 每日保留水滴, 默认80g， 用于完成第二天的10次浇水任务',
        'jd_wishing_pool_code':  '# 众筹许愿池助力码',
        'jd_burning_summer_code':  '# 燃动夏季助力码',
        'jd_smash_golden_egg_code': '# 疯狂砸金蛋助力码',
        'dj_fruit_code': '# 到家果园助力码',
        'jd_grab_bean_code': '# 抢京豆助力码',
    }
    if not old_cfg:
        # 加载配置文件
        with open(CONF_PATH, 'r', encoding='utf-8-sig') as f:
            old_cfg = yaml.safe_load(f)

    if not new_cfg:
        # 读取配置示例文件
        with open(EXAMPLE_CONFIG_PATH, 'r', encoding='utf-8-sig') as f:
            new_cfg = yaml.safe_load(f)

    for key, val in new_cfg.items():
        if key in old_cfg:
            if new_cfg[key] != old_cfg[key]:
                old_cfg[key] = new_cfg[key]
        else:
            old_cfg[key] = new_cfg[key]  # 否则加入到旧配置文件中

    for key in list(old_cfg.keys()):  # 移除已废除的配置项
        if key not in new_cfg:
            old_cfg.pop(key)

    old_cfg['jd_cookies'] = []
    for cookie in JD_COOKIES:
        old_cfg['jd_cookies'].append('pt_pin={};pt_key={};'.format(cookie['pt_pin'], cookie['pt_key']))

    # 备份配置文件
    shutil.copy(CONF_PATH, BAK_CONFIG_PATH)

    # 利用yaml模块写入到配置文件
    with open(CONF_PATH, 'w', encoding='utf-8-sig') as f:
        yaml.dump(old_cfg, stream=f, sort_keys=False)

    # 重新读取并为配置添加注释
    cfg_text = ''
    with open(CONF_PATH, 'r', encoding='utf-8-sig') as f:
        for line in f:
            key = line.strip().split(':')[0]
            if key in comment_map:
                line = '\n' + comment_map[key] + '\n' + line
            cfg_text += line

    # 重新写入配置文件
    with open(CONF_PATH, 'w', encoding='utf-8-sig') as f:
        f.write(cfg_text)


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
        # sorted(code_map.items(), key=lambda kv: (kv[1], kv[0]))
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
            },
            'jd_wishing_pool_code': {
                'cls': JdWishingPool,
                'name': '众筹许愿池'
            },
            'jd_smash_golden_egg_code': {
                'cls': JdSmashGoldenEgg,
                'name': '疯狂砸金蛋'
            },
            'dj_fruit_code': {
                'cls': DjFruit,
                'name': '到家果园'
            },
            'jd_grab_bean_code': {
                'cls': JdGrabBean,
                'name': '抢京豆'
            }

        }
        cfg = cls.read_config()

        for key, val in code_func_map.items():
            code_list = await cls.get_share_code(val['cls'], val['name'])
            cfg[key] = code_list
            # if key == 'jd_cash_code':
            #     cfg[key] = list(set(code_list))
            # else:
            #     cfg[key] = list(set([i for i in (cfg.get(key, []) + code_list) if i is not None and i != 'null']))

        println('助力获取完成, 准备写入配置文件: {}中...'.format(CONF_PATH))
        update_config(cfg, copy.copy(cfg))
        println('成功更新助力码到配置文件:{}中...'.format(CONF_PATH))


if __name__ == '__main__':
    app = UpdateShareCode()
    asyncio.run(app.run())


