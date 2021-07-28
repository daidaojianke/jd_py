#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/19 9:41
# @File    : process.py
# @Project : jd_scripts
from urllib.parse import unquote
import multiprocessing
import random

from utils.console import println
from utils.notify import notify
from config import JD_COOKIES, PROCESS_NUM


def process_start(func, name='', process_num=None):
    """
    从配置中读取JD_COOKIES，开启多进程执行func。
    :param process_num:
    :param name: 活动名称
    :param func: 活动程序入口
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

    pool = multiprocessing.Pool(process_count)
    process_list = []
    println("开始执行{}, 共{}个账号, 启动{}个进程!\n".format(name, len(JD_COOKIES), process_count), style='bold green')

    for i in range(len(JD_COOKIES)):
        jd_cookie = JD_COOKIES[i]
        process = pool.apply_async(func, args=(jd_cookie['pt_pin'], jd_cookie['pt_key'],))
        process_list.append(process)
        println("  {}.账号:{}, 正在进行{}...".format(i + 1, unquote(jd_cookie['pt_pin']), name),
                style=random.choice(['bold yellow', 'bold green']))
    pool.close()

    println("\n{}正在运行, 请耐心等候...\n".format(name), style='bold green')

    pool.join()  # 等待进程结束

    notify_message = ''
    for process in process_list:   # 获取通知
        try:
            message = process.get()
        except:
            continue
        if not message:
            continue
        notify_message += message + '\n'

    if notify_message != '':
        message = '\n======📣{}📣======\n'.format(name) + notify_message
        println(message)
        notify(message)

    println("\n{}执行完毕, 退出程序...".format(name), style='bold green')
