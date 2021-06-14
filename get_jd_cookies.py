#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/14 9:57
# @File    : get_jd_cookies.py
# @Project : jd_scripts
# @Desc    : 京东扫描登录获取cookies
import sys
import time
import qrcode
import requests
from log import get_logger

logger = get_logger('get_jd_cookies')
ANDROID_PLATFORM = 'android'
IOS_PLATFORM = 'ios'
WINDOWS_PLATFORM = 'windows'


def get_timestamp():
    """
    获取当前毫秒时间戳
    :return:
    """
    return int(time.time() * 1000)


class JDCookies:

    def __init__(self, device_platform=ANDROID_PLATFORM, *args, **kwargs):
        """
        :param platform:
        """
        self._platform = device_platform

        self._http = requests.Session()
        self._http.headers = self.__get_headers()

    def __get_headers(self):
        """
        获取请求头
        :return:
        """
        if self._platform == ANDROID_PLATFORM:
            user_agent = 'Mozilla/5.0 (Linux; Android 10; ELS-TN00; HMSCore 5.1.0.309) AppleWebKit/537.36 (KHTML, ' \
                         'like Gecko) Chrome/78.0.3904.108 HuaweiBrowser/11.0.2.306 Mobile Safari/537.36'
        elif self._platform == IOS_PLATFORM:
            user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, ' \
                         'like Gecko) Mobile/16D57'
        elif self._platform == WINDOWS_PLATFORM:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                         'Chrome/71.0.1047.55 Safari/537.36'
        else:
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko)' \
                         'Chrome/63.0.3239.84 Safari/537.36'

        headers = {
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-cn',
            'Referer': 'https://plogin.m.jd.com/login/login?appid=300&returnurl=https://wq.jd.com/passport'
                       '/LoginRedirect?state={}&returnurl=https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc'
                       '=&/myJd/home.action&source=wq_passport'.format(get_timestamp()),
            'User-Agent': user_agent,
            'Host': 'plogin.m.jd.com'
        }
        return headers

    def __login_entrance(self):
        """
        扫描登录入口，先获取s_token
        :return:
        """
        logger.info("正在获取s_token")
        url = 'https://plogin.m.jd.com/cgi-bin/mm/new_login_entrance?lang=chs&appid=300&returnurl=https://wq.jd.com' \
              '/passport/LoginRedirect?state={}&returnurl=https://home.m.jd.com ' \
              '/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(get_timestamp())
        try:
            response = self._http.get(url)
            return response.json()['s_token']
        except requests.RequestException as e:
            logger.info("获取s_token失败, 网络异常: {}".format(e.args))

    def __generate_qr_code(self, s_token=''):
        """
        用s_token生成二维码
        :param s_token:
        :return:
        """
        logger.info("正在获取登录二维码")
        url = 'https://plogin.m.jd.com/cgi-bin/m/tmauthreflogurl?s_token={}&v={}&remember=true'.format(s_token,
                                                                                                       get_timestamp())
        body = 'lang=chs&appid=300&source=wq_passport&returnurl=https://wqlogin2.jd.com/passport/LoginRedirect?state' \
               '={}&returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&' \
               'ufc=&/myJd/home.action'.format(get_timestamp())

        try:
            response = self._http.post(url, body)
            data = response.json()
            token = data['token']
            qr_code_url = 'https://plogin.m.jd.com/cgi-bin/m/tmauth?appid=300&client_type=m&token=' + token
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=4,
                border=1,
            )
            qr.add_data(qr_code_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save('./qrcode.png')
            img.show()
            logger.info("请扫描二维码登录, 3分钟内有效")
            return token

        except requests.RequestException as e:
            logger.info("获取二维码失败, 网络异常: {}".format(e.args))

    def check_login(self, token=''):
        """
        检查登录状态
        :param token:
        :return:
        """
        okl_token = self._http.cookies.get('okl_token')

        url = 'https://plogin.m.jd.com/cgi-bin/m/tmauthchecktoken?&token={}&ou_state=0&okl_token={}'.format(token,
                                                                                                            okl_token)
        body = 'lang=chs&appid=300&source=wq_passport&returnurl=https://wqlogin2.jd.com/passport/LoginRedirect?state' \
               '={}&returnurl=//home.m.jd.com/myJd/' \
               'newhome.action?sceneval=2&ufc=&/myJd/home.action'.format(get_timestamp())
        start_time = int(time.time())

        while True:
            time.sleep(1)
            try:
                response = self._http.post(url, body)
                data = response.json()
                if data['errcode'] == 0:
                    pt_pin = self._http.cookies.get('pt_pin')
                    pt_key = self._http.cookies.get('pt_key')
                    logger.info("成功获取CK: pt_pin={};pt_key={} 退出程序".format(pt_pin, pt_key))
                    break
            except requests.RequestException as e:
                logger.info("获取登录状态失败")
            if int(time.time()) - start_time > 60 * 3:
                logger.info("超过三分钟仍未扫码, 退出程序")
                sys.exit(0)

    def start(self):
        """
        :return:
        """
        s_token = self.__login_entrance()
        token = self.__generate_qr_code(s_token)
        self.check_login(token)


if __name__ == '__main__':
    jd = JDCookies()
    jd.start()
