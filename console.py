#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/16 2:47 下午
# @File    : console.py
# @Project : jd_scripts
# @Desc    :
from rich.console import Console, JustifyMethod, OverflowMethod
from typing import Union, Any
from rich.console import Optional
from rich.style import Style
from config import JD_DEBUG

__all__ = ('println',)

console = Console()


def println(*args, **kwargs):
    """
    控制台打印数据
    :return:
    """
    if JD_DEBUG:
        console.print(*args, **kwargs)


if __name__ == '__main__':
    println('hello world', style='yellow')