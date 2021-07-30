#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/19 9:41
# @File    : process.py
# @Project : jd_scripts
from urllib.parse import unquote
import multiprocessing
import random

from urllib.parse import unquote
from utils.cookie import sync_check_cookie
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

    if process_count < 1:
        println('未配置jd_cookie, 脚本无法运行, 请在conf/config.yaml中配置jd_cookie!')
        return

    pool = multiprocessing.Pool(process_count)
    process_list = []
    println("开始执行{}, 共{}个账号, 启动{}个进程!\n".format(name, len(JD_COOKIES), process_count), style='bold green')

    for i in range(len(JD_COOKIES)):
        jd_cookie = JD_COOKIES[i]
        account = unquote(jd_cookie['pt_pin'])
        # println('{}, 正在检测cookie状态!'.format(account))
        ok = sync_check_cookie(jd_cookie)
        if not ok:
            println('{}.账号:{}, cookie已过期, 无法执行:{}!'.format(i+1, account, name))
            continue
        process = pool.apply_async(func, args=(jd_cookie['pt_pin'], jd_cookie['pt_key'],))
        process_list.append(process)
        println("  {}.账号:{}, 正在进行{}...".format(i + 1, account, name),
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
        title = '\n======📣{}📣======\n'.format(name)
        notify(title, notify_message)

    # if '宠汪汪' in name:  # 杀浏览器进程
    #     os.system("ps -ef |grep chrome |grep -v ^root |awk '{print $2}' | xargs kill")

    println("\n{}执行完毕, 退出程序...".format(name), style='bold green')
