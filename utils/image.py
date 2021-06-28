#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/28 5:00 下午
# @File    : image.py
# @Project : jd_scripts
# @Desc    :
import re
import base64
import cv2

def save_img(b64_str, img_path=''):
    """
    base64字符串保存为图片
    :param img_path:
    :param b64_str:
    :return:
    """
    b64_str = re.sub('^data:image/.+;base64,', '', b64_str)
    img_str = base64.b64decode(b64_str)
    with open(img_path, 'wb') as f:
        f.write(img_str)
    return img_path


def _tran_canny(image):
    """消除噪声"""
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return cv2.Canny(image, 50, 150)


def detect_displacement(img_slider_path, image_background_path, img_slider_dim=(38, 38), img_bg_dim=(105, 270)):
    """detect displacement"""
    # # 参数0是灰度模式
    image = cv2.imread(img_slider_path, 0)
    template = cv2.imread(image_background_path, 0)

    image = cv2.resize(image, img_slider_dim, interpolation=cv2.INTER_AREA)
    template = cv2.resize(template, img_bg_dim, interpolation=cv2.INTER_AREA)

    # 寻找最佳匹配
    res = cv2.matchTemplate(_tran_canny(image), _tran_canny(template), cv2.TM_CCOEFF_NORMED)
    # 最小值，最大值，并得到最小值, 最大值的索引
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc[0]  # 横坐标
    # 展示圈出来的区域
    x, y = max_loc  # 获取x,y位置坐标

    w, h = image.shape[::-1]  # 宽高
    cv2.rectangle(template, (x, y), (x + w, y + h), (7, 249, 151), 2)
    # show(template)
    return top_left + 1
