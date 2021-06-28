#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/28 5:53 下午
# @File    : test.py
# @Project : jd_scripts
# @Desc    :
from utils.image import detect_displacement
from config import IMAGES_DIR
import os

if __name__ == '__main__':
    res = detect_displacement(os.path.join(IMAGES_DIR, 'jd_pet_dog_slider.png'),
                              os.path.join(IMAGES_DIR, 'jd_pet_dog_bg.png'))
    print(res)