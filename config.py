#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/16 11:31 上午
# @File    : conf.py
# @Project : jd_scripts
# @Desc    : 脚本配置文件
import os
import sys
import re
import yaml
import platform

# 项目根目录
BASE_DIR = os.path.split(os.path.abspath(sys.argv[0]))[0]

# 日志目录
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 示例配置文件路径
EXAMPLE_CONFIG_PATH = os.path.join(BASE_DIR, 'conf/.config_example.yaml')

# 备份配置文件路径
BAK_CONFIG_PATH = os.path.join(BASE_DIR, 'conf/config.yaml.bak')

# 配置文件路径
CONF_PATH = os.path.join(BASE_DIR, 'conf/config.yaml')

IMAGES_DIR = os.path.join(BASE_DIR, 'static/images')

if platform.system() == 'Windows':
    IMAGES_DIR = IMAGES_DIR.replace('/', '\\')

# 创建日志文件夹
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 创建图片资源文件夹
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# 加载配置文件
with open(CONF_PATH, 'r', encoding='utf-8-sig') as f:
    cfg = yaml.safe_load(f)

# 是否开启调试模式, 关闭不会显示控制台输出
JD_DEBUG = cfg.get('debug', True)

# 默认进程数量
PROCESS_NUM = cfg.get('process_num', 4)

# JD COOKIES
JD_COOKIES = [j for j in [{'pt_pin': re.search('pt_pin=(.*?);', i).group(1),
                           'pt_key': re.search('pt_key=(.*?);', i).group(1)}
              for i in cfg.get('jd_cookies', []) if re.search('pt_pin=(.*?);pt_key=(.*?);', i)
              or re.search('pt_key=(.*?);pt_pin=(.*?);', i)] if j['pt_pin'] != '']

# 默认请求头
DEFAULT_USER_AGENT = 'jdapp;iPhone;12.0.1;15.1.1;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS ' \
                     'X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'

# 请求头
USER_AGENT = cfg.get('user_agent', None) if cfg.get('user_agent', None) else DEFAULT_USER_AGENT

# 种豆得豆互助码
JD_PLANTING_BEAN_CODE = list(set(cfg.get('jd_planting_bean_code') if cfg.get('jd_planting_bean_code') else []))
JD_PLANTING_BEAN_CODE.append('mlrdw3aw26j3x3vxi2qvp7xj5llrsmtd3tde64i')

# 东东农场互助码
JD_FARM_CODE = list(set(cfg.get('jd_farm_code') if cfg.get('jd_farm_code') else []))
JD_FARM_CODE.append('f9a5389ab473423e83a746e03a82dddc')

# 东东农场是否使用水滴换豆卡
JD_FARM_BEAN_CARD = cfg.get('jd_farm_bean_card') if cfg.get('jd_farm_bean_card') else False

# 东东农场保留水滴用于明天浇水完成十次浇水任务
JD_FARM_RETAIN_WATER = cfg.get('jd_farm_retain_water') if cfg.get('jd_farm_retain_water') else 80

# 京东金融摇钱树助力码
JR_MONEY_TREE_CODE = list(set(cfg.get('jr_money_tree_code') if cfg.get('jr_money_tree_code') else []))
JR_MONEY_TREE_CODE.append('GEwzybOwKgTmY4q07j9ZiMAdoUJQ3Dik')

# 东东工厂助力码
JD_FACTORY_CODE = list(set(cfg.get('jd_factory_code') if cfg.get('jd_factory_code') else []))
JD_FACTORY_CODE.append('T0225KkcRRYR_QbSIkmgkPUDJQCjVWnYaS5kRrbA')

# 东东萌宠互助码
JD_CUTE_PET_CODE = list(set(cfg.get('jd_cute_pet_code') if cfg.get('jd_cute_pet_code') else []))
JD_CUTE_PET_CODE.append('MTAxNzIxMDc1MTAwMDAwMDA0OTQ4ODA1Mw==')

# 京东领现金互助码
JD_CASH_CODE = list(set(cfg.get('jd_cash_code') if cfg.get('jd_cash_code') else []))
JD_CASH_CODE.append('eU9YaeS6bq4j8z2Bz3Eahw@IRs1bey1Z_0')


# 众筹许愿池助力码
JD_WISHING_POOL_CODE = list(set(cfg.get('jd_wishing_pool_code') if cfg.get('jd_wishing_pool_code') else []))
JD_WISHING_POOL_CODE.append('T0225KkcRRYR_QbSIkmgkPUDJQCjRXnYaU5kRrbA')

# 燃动夏季互助码
JD_BURNING_SUMMER_CODE = list(set(cfg.get('jd_burning_summer_code') if cfg.get('jd_burning_summer_code') else []))
JD_BURNING_SUMMER_CODE.append('HcmphLbwLg-rdovIEtZgglnd0kl-mHlZa0Ke_B87Q4TD1WVgIqaoiXX1QhzVv6-3sgm6uBAKzq2l_Ym0jB6fZQ')

# 疯狂砸金蛋助力码
JD_SMASH_GOLDEN_EGG_CODE = list(set(cfg.get('jd_smash_golden_egg_code') if cfg.get('jd_smash_golden_egg_code') else []))

# TG 用户ID
TG_USER_ID = cfg.get('notify', dict()).get('tg_user_id', None)
# TG 机器人Token
TG_BOT_TOKEN = cfg.get('notify', dict()).get('tg_bot_token', None)

JD_BEAN_INDIANA_OPEN = cfg.get('jd_bean_indiana', False)

