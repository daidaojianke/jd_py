#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/16 4:10 下午
# @File    : notify.py
# @Project : jd_scripts
# @Desc    : 通知模块
import requests
import telegram
from config import TG_BOT_TOKEN, TG_USER_ID, PUSH_P_TOKEN
from utils.console import println


def push_plus_notify(title, content):
    """
    :return:
    """
    try:
        if not PUSH_P_TOKEN:
            println('未配置PUSH+ token, 不推送PUSH+信息!')
            return
        url = 'http://pushplus.hxtrip.com/send'

        headers = {
            'Content-Type': 'application/json',
        }
        content = content.replace('\n', '<br>')
        data = {
            'token': PUSH_P_TOKEN,
            'title': title,
            'content': content,
            'template': 'html'
        }

        response = requests.post(url=url, json=data, headers=headers)
        response_data = response.json()
        if response_data['code'] == 200:
            println('成功推送消息至PUSH+')
        else:
            println('推送PUSH+消息失败, {}'.format(response_data))
    except Exception as e:
        println('推送PUSH+数据失败, {}!'.format(e.args))


def tg_bot_notify(message):
    """
    :return:
    """
    if TG_BOT_TOKEN and TG_USER_ID:
        try:
            bot = telegram.Bot(TG_BOT_TOKEN)
            bot.send_message(TG_USER_ID, message)
            println('\n成功推送消息到TG!')
        except Exception as e:
            println('\nTG消息通知异常:{}'.format(e.args))
    else:
        println("\n未配置TG_BOT_TOKEN和TG_USER_ID, 不推送TG消息...")


def notify(title, content):
    """
    消息推送
    :param content:
    :param title:
    :param message:
    :return:
    """
    push_plus_notify(title, content)
    # TG通知
    tg_bot_notify(title + '\n' + content)

