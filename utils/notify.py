#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/16 4:10 下午
# @File    : notify.py
# @Project : jd_scripts
# @Desc    : 通知模块
import telebot
from config import TG_BOT_TOKEN, TG_USER_ID
from console import println


def push_message_to_tg(message):
    """
    推送消息到TG机器人
    :param message:
    :return:
    """
    if TG_BOT_TOKEN and TG_USER_ID:
        bot = telebot.TeleBot(TG_BOT_TOKEN)
        bot.send_message(TG_USER_ID, message)
    else:
        println("未配置TG_BOT_TOKEN和TG_USER_ID, 不推送TG消息...")

