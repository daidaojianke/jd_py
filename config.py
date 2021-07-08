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

if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# 加载配置文件
with open(CONF_PATH, 'r', encoding='utf-8-sig') as f:
    cfg = yaml.safe_load(f)

# 是否开启调试模式, 关闭不会显示控制台输出
JD_DEBUG = cfg.get('debug', True)

PROCESS_NUM = cfg.get('process_num', 4)

# JD COOKIES
JD_COOKIES = [{'pt_pin': re.search('pt_pin=(.*?);', i).group(1), 'pt_key': re.search('pt_key=(.*?);', i).group(1)}
              for i in cfg.get('jd_cookies', []) if re.search('pt_pin=(.*?);pt_key=(.*?);', i)
              or re.search('pt_key=(.*?);pt_pin=(.*?);', i)]

DEFAULT_USER_AGENT = 'jdapp;iPhone;12.0.1;15.1.1;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS ' \
                     'X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'

# 请求头
USER_AGENT = cfg.get('user_agent', None) if cfg.get('user_agent', None) else DEFAULT_USER_AGENT

JD_PLANTING_CODE = cfg.get('jd_planting_code') if cfg.get('jd_planting_code') else []
JD_PLANTING_CODE.append('t7obxmpebrxkdnfmcaebbfbrvem3hdr6ej6227y')
JD_PLANTING_CODE = list(set(JD_PLANTING_CODE))

JD_FARM_CODE = cfg.get('jd_farm_code') if cfg.get('jd_farm_code') else []
JD_FARM_CODE = list(set(JD_FARM_CODE))
JD_FARM_BEAN_CARD = cfg.get('jd_farm_bean_card') if cfg.get('jd_farm_bean_card') else False
JD_FARM_RETAIN_WATER = cfg.get('jd_farm_retain_water') if cfg.get('jd_farm_retain_water') else 80


JD_MONEY_TREE_SHARE_PIN = list(set(cfg.get('jd_money_tree_share_pin') if cfg.get('jd_money_tree_share_pin') else []))

JD_FACTORY_SHARE_CODE = list(set(cfg.get('jd_factory_share_code') if cfg.get('jd_factory_share_code') else []))

JD_CUTE_PET_SHARE_CODE = list(set(cfg.get('jd_cute_pet_code') if cfg.get('jd_cute_pet_code') else []))

# TG 用户ID
TG_USER_ID = cfg.get('notify', dict()).get('tg_user_id', None)
# TG 机器人Token
TG_BOT_TOKEN = cfg.get('notify', dict()).get('tg_bot_token', None)


