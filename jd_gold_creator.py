#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/13 1:58 下午
# @File    : jd_gold_creator.py
# @Project : jd_scripts
# @Desc    : 京东APP->排行榜->金榜创造营
import asyncio
import aiohttp
import json
import re
import random

from urllib.parse import unquote, quote
from config import USER_AGENT
from utils.console import println


class JdGoldCreator:

    headers = {
        'referer': 'https://h5.m.jd.com/babelDiy/Zeus/2H5Ng86mUJLXToEo57qWkJkjFPxw/index.html',
        'user-agent': USER_AGENT,
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key
        }
        self._pt_pin = unquote(pt_pin)

    async def request(self, session, function_id, body=None):
        try:
            if body is None:
                body = {}
            url = 'https://api.m.jd.com/client.action?functionId={}&body={}' \
                  '&appid=content_ecology&clientVersion=10.0.6&client=wh5' \
                  '&jsonp=jsonp_kr1mdm3p_12m_29&eufv=false'.format(function_id, quote(json.dumps(body)))
            response = await session.post(url=url)
            text = await response.text()
            temp = re.search(r'\((.*)\);', text).group(1)
            data = json.loads(temp)
            return data
        except Exception as e:
            println('{}, 获取数据失败:{}'.format(self._pt_pin, e.args))
            return None

    async def get_index_data(self, session):
        """
        获取获得首页数据
        :param session:
        :return:
        """
        return await self.request(session, 'goldCreatorTab', {"subTitleId": "", "isPrivateVote": "0"})

    async def do_vote(self, session, index_data):
        """
        进行投票
        :param session:
        :param index_data:
        :return:
        """
        subject_list = index_data['result']['subTitleInfos']
        stage_id = index_data['result']['mainTitleHeadInfo']['stageId']
        for subject in subject_list:
            body = {
                "groupId": subject['matGrpId'],
                "stageId": stage_id,
                "subTitleId": subject['subTitleId'],
                "batchId": subject['batchId'],
                "skuId": "",
                "taskId": int(subject['taskId']),
            }
            res = await self.request(session, 'goldCreatorDetail', body)
            if res['code'] != '0':
                println('{}, 获取主题:《{}》商品列表失败!'.format(self._pt_pin, subject['shortTitle']))
            else:
                println('{}, 获取主题:《{}》商品列表成功, 开始投票!'.format(self._pt_pin, subject['shortTitle']))

            task_list = res['result']['taskList']
            sku_list = res['result']['skuList']
            item_id = res['result']['signTask']['taskItemInfo']['itemId']
            sku = random.choice(sku_list)
            body = {
                "stageId": stage_id,
                "subTitleId": subject['subTitleId'],
                "skuId": sku['skuId'],
                "taskId": int(subject['taskId']),
                "itemId": item_id,
                "rankId": sku["rankId"],
                "type": 1,
                "batchId": subject['batchId'],
            }
            res = await self.request(session, 'goldCreatorDoTask', body)

            if res['code'] != '0':
                println('{}, 为商品:《{}》投票失败!'.format(self._pt_pin, sku['name']))
            else:
                if 'lotteryCode' in res['result'] and res['result']['lotteryCode'] != '0':
                    println('{}, 为商品:《{}》投票失败, {}'.format(self._pt_pin, sku['name'], res['result']['lotteryMsg']))
                elif 'taskCode' in res['result'] and res['result']['taskCode'] == '103':
                    println('{}, 为商品: 《{}》投票失败, {}!'.format(self._pt_pin, sku['name'], res['result']['taskMsg']))
                else:
                    println('{}, 为商品:《{}》投票成功, 获得京豆:{}'.format(self._pt_pin, sku['name'], res['result']['lotteryScore']))

            for task in task_list:
                if task[0]['taskStatus'] == 2:
                    continue
                body = {
                    "taskId": int(task[0]['taskId']),
                    "itemId": task[0]['taskItemInfo']['taskId'],
                    "type": 2,
                    "batchId": subject['batchId']
                }
                res = await self.request(session, 'goldCreatorDoTask', body)
                println('{}, 做额外任务: 《{}》, 结果:{}!'.format(self._pt_pin, task[0]['taskItemInfo']['title'], res))

            await asyncio.sleep(1)

    async def run(self):
        """
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            data = await self.get_index_data(session)
            if not data or data['code'] != '0':
                println('{}, 获取首页数据失败, 退出程序!'.format(self._pt_pin))
                return
            await self.do_vote(session, index_data=data)  # 投票


def start(pt_pin, pt_key, name='金榜创造营'):
    """
    :param name:
    :param pt_pin:
    :param pt_key:
    :return:
    """
    try:
        app = JdGoldCreator(pt_pin, pt_key)
        asyncio.run(app.run())
    except Exception as e:
        message = '【活动名称】{}\n【京东账号】{}【运行异常】{}\n'.format(name,  pt_pin,  e.args)
        return message


if __name__ == '__main__':
    from utils.process import process_start
    process_start(start, '金榜创造营')
