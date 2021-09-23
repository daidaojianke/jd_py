#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/22 3:09 下午
# @File    : update_nodejs.py
# @Project : jd_scripts
# @Desc    : 集成更新nodejs库
import os
from config import BASE_DIR, JS_REPO_LIST


def update():
    """
    :return:
    """
    for repo_name, repo_url in JS_REPO_LIST.items():
        repo_path = os.path.join(BASE_DIR, repo_name)
        if os.path.exists(repo_path):
            os.system('git pull;')
        else:
            os.system('git clone {} {};'.format(repo_url, repo_path))

        os.system('cd {} && npm install;tsc *.ts'.format(repo_path))


if __name__ == '__main__':
    update()
