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

# 项目根目录
BASE_DIR = os.path.abspath(os.path.splitdrive(sys.argv[0])[0])

# 日志目录
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 配置文件路径
CONF_PATH = os.path.join(BASE_DIR, 'conf/config.yaml')

# 加载配置文件
with open('conf/config.yaml', 'r') as f:
    cfg = yaml.safe_load(f)

# 是否开启调试模式, 关闭不会显示控制台输出
JD_DEBUG = cfg.get('JD_DEBUG', True)

# JD COOKIES
JD_COOKIES = [{'pt_pin': re.search('pt_pin=(.*?);', i).group(1), 'pt_key': re.search('pt_key=(.*?);', i).group(1)}
              for i in cfg.get('jd_cookies', []) if re.search('pt_pin=(.*?);pt_key=(.*?);', i)
              or re.search('pt_key=(.*?);pt_pin=(.*?);', i)]

DEFAULT_USER_AGENT = 'jdapp;iPhone;12.0.1;15.1.1;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_1_1 like Mac OS ' \
                     'X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'

# 请求头
USER_AGENT = cfg.get('user_agent', None) if cfg.get('user_agent', None) else DEFAULT_USER_AGENT

# TG 用户ID
TG_USER_ID = cfg.get('notify', dict()).get('tg_user_id', None)
# TG 机器人Token
TG_BOT_TOKEN = cfg.get('notify', dict()).get('tg_bot_token', None)
