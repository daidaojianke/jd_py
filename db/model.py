#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/29 1:19 下午
# @File    : model.py
# @Project : jd_scripts
# @Desc    :
from datetime import datetime
from peewee import *
from config import DB_PATH

db = SqliteDatabase(DB_PATH)


class Code(Model):
    """
    邀请/助力码
    """
    account = CharField(verbose_name='京东账号', max_length=255)

    # 邀请/助力码类型L: 1容器内部账号助力码, 2云端助力码, 3,容器配置填写助力码
    code_type = SmallIntegerField(verbose_name='邀请/助力码标示', default=0)

    code_key = CharField(verbose_name='邀请/助力码标示', max_length=30)

    code_val = TextField(verbose_name='邀请/助力码内容')

    sort = SmallIntegerField(verbose_name='排序字段', default=1)

    created_at = DateField(verbose_name='创建日期')

    updated_at = DateField(verbose_name='更新日期')

    class Meta:
        database = db
        table_name = 'code'

    @classmethod
    def insert_code(cls, code_key=None, account='', code_val='', code_type=1):
        """
        插入助力码
        :param code_val:
        :param account:
        :param code_key:
        :param code_type:
        :return:
        """
        rowid = (cls.insert(code_key=code_key, account=account, code_val=code_val, code_type=code_type)
                 .on_conflict(preserve=[cls.account, cls.code_type, cls.code_val]).execute())
        print(rowid)

    @classmethod
    def get_first_code(cls, code_key='', exclude_account=None):
        """
        获取第一条助力码
        :param code_key: 助力码类型
        :param exclude_account: 排除账号
        :return:
        """
        pass

    @classmethod
    def get_code_list(cls, code_key='', exclude_account=None):
        """
        获取助力码列表
        :param code_key: 助力码类型
        :param exclude_account: 排除账号
        :return:
        """
        pass


db.connect()

db.create_tables([Code])
