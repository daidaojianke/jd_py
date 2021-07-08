#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/8 4:27 下午
# @File    : update_config.py.py
# @Project : jd_scripts
# @Desc    : 更新配置脚本
import shutil
import yaml
from config import CONF_PATH, EXAMPLE_CONFIG_PATH, BAK_CONFIG_PATH


def update_config(old_cfg=None, new_cfg=None):
    """
    更新配置文件
    :return:
    """
    comment_map = {
        'debug': '# 控制输出, true打开输出, false关闭输出',
        'process_num': '# 开启多个进程',
        'jd_cookies': '# 京东账号Cookies, 一行一个, 优先排在助力前面的!',
        'jd_planting_code': '# 种豆得豆互助码, 一行一个, 优先排在助力前面的!',
        'jd_cute_pet_code': '# 东东萌宠互助码, 一行一个, 优先排在助力前面的!',
        'jd_factory_share_code': '# 东东工厂互助码, 一行一个, 优先排在助力前面的!',
        'jd_farm_code': '# 东东农场互助码, 一行一个, 优先排在助力前面的!',
        'jd_money_tree_share_pin': '# 金果摇钱树互助码, 一行一个, 优先排在助力前面的!',
        'jd_sgmh_share_code': '# 闪购盲盒互助码, 一行一个, 优先排在助力前面的!',
        'jx_factory_share_code': '# 京喜工厂互助码， 一行一个, 优先排在助力前面的!',
        'jx_farm_share_code': '# 京喜农场互助码, 一行一个, 优先排在助力前面的!',
        'notify': '# TG消息通知配置',
        'user_agent': '# 请求头, 需要替换自行抓包, 否则不填使用默认即可',
        'tg_bot_token': '# TG 机器人Token',
        'tg_user_id': '# TG用户ID',
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
        if key in old_cfg:  # 如果在旧配置文件存在的配置跳过
            continue
        else:
            old_cfg[key] = new_cfg[key]  # 否则加入到旧配置文件中

    # 排序
    sorted(old_cfg)

    # 备份配置文件
    shutil.copy(CONF_PATH, BAK_CONFIG_PATH)

    # 利用yaml模块写入到配置文件
    with open(CONF_PATH, 'w', encoding='utf-8-sig') as f:
        yaml.dump(old_cfg, f)

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


if __name__ == '__main__':
    update_config()