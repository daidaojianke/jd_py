#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/31 下午1:15
# @Project : jd_scripts
# @File    : update_default_crontab.py
# @Desc    : 根据注释@Cron生成default_crontab.sh!
import os
import sys
import re


def get_script_list(dir_path=None):
    """
    获取脚本列表
    :return:
    """
    script_list = []
    if not dir_path:
        return script_list
    file_list = [file for file in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, file))]
    for filename in file_list:
        if not filename.split('_')[0] in ['jr', 'dj', 'jx', 'jd']:
            continue
        script_list.append(filename)

    script_list.sort()

    return script_list


def find_cron(script_path):
    """
    查找脚本文件中的cron任务
    :param script_path:
    :return:
    """
    script_filename = os.path.split(script_path)[-1]
    script_name = os.path.splitext(script_filename)[0]
    with open(script_path, 'r') as f:
        text = '\n'.join(f.readlines()[:10])
        search = re.search(r'Cron.*:(.*)', text)
        if not search:
            return None
        cron = search.group(1).strip()

        if cron.startswith('#'):  # 已经关闭的脚本
            return None

        crontab = r'{} /scripts/{} >> /scripts/logs/{}_`date "+\%Y-\%m-\%d"`.log 2>&1'. \
            format(cron, script_filename, script_name)

        comment = re.search(r'@Desc.*:(.*)', text)
        if comment:
            result = '# {}\n{}\n\n'.format(comment.group(1), crontab)
        else:
            result = '{}\n\n'.format(crontab)
        return result


def generate_default_crontab(output='default_crontab.sh'):
    """
    生成默认的定时任务
    :return:
    """
    pwd = os.path.split(os.path.abspath(sys.argv[0]))[0].replace('tools', '')
    script_list = get_script_list(pwd)

    crontab_headers = [
        '# 默认定时任务\n\n'
        'SHELL=/bin/sh\n\n'
        'PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n\n'
    ]
    crontab_list = [
        '# 定时更新脚本\n30 15 * * * /bin/docker-entrypoint >> /dev/null  2>&1\n\n',
        '# 每2个小时检查一次cookies是否过期\n0 */2 * * * /scripts/check_cookies.py >> /scripts/logs/check_cookies_`date '
        '"+\%Y-\%m-\%d"`.log 2>&1\n\n',
    ]
    for script in script_list:
        filepath = os.path.join(pwd, script)
        crontab = find_cron(filepath)
        if not crontab:
            continue
        crontab_list.append(crontab)

    output = os.path.join(pwd, 'shell/{}'.format(output))
    with open(output, 'w+') as f:
        f.writelines(crontab_headers)
        f.writelines(crontab_list)


if __name__ == '__main__':
    generate_default_crontab()
