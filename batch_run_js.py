#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/22 3:32 下午
# @File    : batch_run_js.py
# @Project : jd_scripts
# @Cron    : 6 6 * * *
# @Desc    : 批量执行JS脚本
import multiprocessing
import os
from config import JS_REPO_LIST, JS_EXECUTE_LIST, BASE_DIR, PROCESS_NUM, JD_COOKIES
from utils.cookie import export_cookie_env


def get_scripts():
    """
    获取需要运行的JS脚本列表
    :return:
    """
    script_list = []
    for repo_name in JS_REPO_LIST.keys():
        for item in JS_EXECUTE_LIST:
            if os.path.exists(item):  # 绝对路径
                script_list.append(item)
            else:  # 相对路径
                if not item.endswith('.js'):
                    item += '.js'
                script_path = os.path.join(BASE_DIR, f'{repo_name}/{item}')
                if not os.path.exists(script_path):
                    continue
                script_list.append(script_path)
        return script_list


def run(script_path):
    """
    :param script_path:
    :return:
    """
    script_dir, script_name = os.path.split(script_path)

    print('************开始执行脚本{}************'.format(script_name))
    print(script_dir, script_name)
    os.system(f'cd {script_dir};node {script_name};')
    print('************脚本:{}执行完毕***********'.format(script_name))


if __name__ == '__main__':
    export_cookie_env(JD_COOKIES)
    scripts = get_scripts()

    pool = multiprocessing.Pool(processes=PROCESS_NUM)  # 进程池
    for script in scripts:
        pool.apply_async(func=run, args=(script,))

    pool.close()
    pool.join()
