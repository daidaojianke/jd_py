#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/28 5:53 下午
# @File    : test.py
# @Project : jd_scripts
# @Desc    :
from furl import furl
from utils.console import println
u = furl('https://api.m.jd.com/client.action?functionId=queryVkComponent&adid=0E38E9F1-4B4C-40A4-A479-DD15E58A5623&area=19_1601_50258_51885&body={"componentId":"4f953e59a3af4b63b4d7c24f172db3c3","taskParam":"{\"actId\":\"8tHNdJLcqwqhkLNA8hqwNRaNu5f\"}","cpUid":"8tHNdJLcqwqhkLNA8hqwNRaNu5f","taskSDKVersion":"1.0.3","businessId":"babel"}&build=167436&client=apple&clientVersion=9.2.5&d_brand=apple&d_model=iPhone11,8&eid=eidIf12a8121eas2urxgGc+zS5+UYGu1Nbed7bq8YY+gPd0Q0t+iviZdQsxnK/HTA7AxZzZBrtu1ulwEviYSV3QUuw2XHHC+PFHdNYx1A/3Zt8xYR+d3&isBackground=N&joycious=228&lang=zh_CN&networkType=wifi&networklibtype=JDNetworkBaseAF&openudid=88732f840b77821b345bf07fd71f609e6ff12f43&osVersion=14.2&partner=TF&rfs=0000&scope=11&screen=828*1792&sign=792d92f78cc893f43c32a4f0b2203a41&st=1606533009673&sv=122&uts=0f31TVRjBSsqndu4/jgUPz6uymy50MQJFKw5SxNDrZGH4Sllq/CDN8uyMr2EAv+1xp60Q9gVAW42IfViu/SFHwjfGAvRI6iMot04FU965+8UfAPZTG6MDwxmIWN7YaTL1ACcfUTG3gtkru+D4w9yowDUIzSuB+u+eoLwM7uynPMJMmGspVGyFIgDXC/tmNibL2k6wYgS249Pa2w5xFnYHQ==&uuid=hjudwgohxzVu96krv/T6Hg==&wifiBssid=1b5809fb84adffec2a397007cc235c03')

data = {
    'functionId': 'queryVkComponent',
    'adid': '0E38E9F1-4B4C-40A4-A479-DD15E58A5623',
    'area': '19_1601_50258_51885',
    'body': {
        "componentId": "4f953e59a3af4b63b4d7c24f172db3c3",
        "taskParam": {"actId": "8tHNdJLcqwqhkLNA8hqwNRaNu5f"},
        "cpUid": "8tHNdJLcqwqhkLNA8hqwNRaNu5f",
        "taskSDKVersion": "1.0.3",
        "businessId": "babel"},
    'build': '167436',
    'client': 'apple',
    'clientVersion': '9.2.5',
    'eid': 'eidIf12a8121eas2urxgGc zS5 UYGu1Nbed7bq8YY gPd0Q0t iviZdQsxnK/HTA7AxZzZBrtu1ulwEviYSV3QUuw2XHHC PFHdNYx1A/3Zt8xYR d3',
    'isBackground': 'N',
    'joycious': '228',
    'openudid': '88732f840b77821b345bf07fd71f609e6ff12f43',
    'osVersion': '14.2',
    'partner': 'TF',
    'rfs': '0000',
    'scope': '11',
    'screen': '828*1792',
    'sign': '792d92f78cc893f43c32a4f0b2203a41',
    'st': '1606533009673',
    'sv': '122',
    'uuid': 'hjudwgohxzVu96krv/T6Hg==', 'wifiBssid': '1b5809fb84adffec2a397007cc235c03'
}
