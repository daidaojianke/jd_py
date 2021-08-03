#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/19 9:41
# @File    : process.py
# @Project : jd_scripts
# @Desc    : 多进程执行脚本

import multiprocessing
import asyncio
import random
from urllib.parse import unquote
from utils.cookie import sync_check_cookie
from utils.console import println
from utils.notify import notify
from utils.logger import logger
from config import JD_COOKIES, PROCESS_NUM

__all__ = ('process_start', )


def start(script_cls, **kwargs):
    """
    任务入口函数
    :param script_cls: 脚本对应类
    :param kwargs: 其他参数
    :return:
    """
    account, name = kwargs.get('account'), kwargs.get('name')
    try:
        println('{}, 开始执行{}...'.format(account, name))
        app = script_cls(**kwargs)
        asyncio.run(app.run())
        println('{}, {}执行完成...'.format(account, name))
        if app.message:
            return app.message
    except Exception as e:

        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  account,  e.args)
        return message


def start_help(script_cls, **kwargs):
    """
    助力入口函数
    :param script_cls:
    :param kwargs:
    :return:
    """
    account, name = kwargs.get('account'), kwargs.get('name')
    try:
        println('{}, 开始{}-助力好友!'.format(account, name))
        app = script_cls(**kwargs)
        asyncio.run(app.run_help())
        println('{}, 完成{}-助力好友!'.format(account, name))
    except Exception as e:
        message = '【活动名称】{}-助力好友\n【京东账号】{}【运行异常】{}\n'.format(name,  account,  e.args)
        return message


def process_start(scripts_cls, name='', process_num=None):
    """
    从配置中读取JD_COOKIES，开启多进程执行func。
    :param scripts_cls: 脚本类
    :param process_num: 进程数量
    :param name: 活动名称
    :return:
    """
    multiprocessing.freeze_support()
    process_count = multiprocessing.cpu_count()

    if process_count < PROCESS_NUM:
        process_count = PROCESS_NUM

    if process_count > len(JD_COOKIES):
        process_count = len(JD_COOKIES)

    if process_num:
        process_count = process_num

    if process_count < 1:
        println('未配置jd_cookie, 脚本无法运行, 请在conf/config.yaml中配置jd_cookie!')
        return

    pool = multiprocessing.Pool(process_count)  # 进程池
    process_list = []  # 进程列表

    println("开始执行{}, 共{}个账号, 启动{}个进程!\n".format(name, len(JD_COOKIES), process_count), style='bold green')

    kwargs_list = []

    for i in range(len(JD_COOKIES)):
        jd_cookie = JD_COOKIES[i]
        account = unquote(jd_cookie['pt_pin'])
        ok = sync_check_cookie(jd_cookie)
        if not ok:  # 检查cookies状态, 这里不通知, 有定时任务会通知cookies过期!
            println('{}.账号:{}, cookie已过期, 无法执行:{}!'.format(i+1, account, name))
            continue
        kwargs = {
            'name': name,
            'sort': i,   # 排序, 影响助力码顺序
            'account': account
        }
        kwargs.update(jd_cookie)
        kwargs_list.append(kwargs)
        process = pool.apply_async(start, args=(scripts_cls, ), kwds=kwargs)
        process_list.append(process)

    pool.close()
    pool.join()  # 等待进程结束

    notify_message = ''   # 消息通知内容

    for process in process_list:   # 获取通知
        try:
            message = process.get()
        except Exception as e:
            logger.error(e.args)
            continue
        if not message:
            continue
        notify_message += message + '\n'

    if hasattr(scripts_cls, 'run_help'):
        pool = multiprocessing.Pool(process_count)  # 进程池
        for kwargs in kwargs_list:
            pool.apply_async(start_help, args=(scripts_cls,), kwds=kwargs)

        pool.close()
        pool.join()  # 等待进程结束

    if notify_message != '':
        title = '\n======📣{}📣======\n'.format(name)
        notify(title, notify_message)

    println('\n所有账号均执行完{}, 退出程序\n'.format(name))
