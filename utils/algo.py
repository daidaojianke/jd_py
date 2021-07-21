#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/21 4:50 下午
# @File    : algo.py
# @Project : jd_scripts
# @Desc    : 加密算法
import hashlib
import hmac
import random
import time


def hmacSha256(key, value):
    """
    sha256加密
    """
    obj = hmac.new(value.encode(), key.encode(), hashlib.sha256)
    return obj.hexdigest()


def hmacSha512(key, value):
    """
    :param key:
    :param value:
    :return:
    """
    obj = hmac.new(value.encode(), key.encode(), hashlib.sha512)
    return obj.hexdigest()


def md5(value):
    """
    :param value:
    :return:
    """
    obj = hashlib.md5()
    obj.update(value.encode())
    return obj.hexdigest()


def sha512(value):
    """
    :param value:
    :return:
    """
    obj = hashlib.sha512()
    obj.update(value.encode())
    return obj.hexdigest()


def sha256(value):
    """
    :param value:
    :return:
    """
    obj = hashlib.sha256()
    obj.update(value.encode())
    return obj.hexdigest()


def hmacMD5(key, value):
    """
    :param key:
    :param value:
    :return:
    """
    obj = hmac.new(value.encode(), key.encode('utf-8'), hashlib.md5)
    return obj.hexdigest()


def generate_fp():
    """
    生成获取签名算法参数的请求参数
    """
    e = "0123456789"
    a = 13
    i = ''
    while a > 0:
        i += e[int(random.random() * len(e)) | 0]
        a -= 1
    i += str(int(time.time()*100))
    return i[0:16]
