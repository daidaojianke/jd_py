#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/6/14 9:57
# @File    : get_jd_cookies.py
# @Project : jd_scripts
# @Desc    : 京东APP扫码登录获取cookies
import time
import qrcode
import requests
from rich.console import Console

console = Console()


def println(*args, **kwargs):
    """
    控制台打印数据
    :return:
    """
    style = kwargs.get('style', 'bold red')
    kwargs['style'] = style
    console.print(*args, **kwargs)


def get_timestamp():
    """
    获取当前毫秒时间戳
    :return:
    """
    return int(time.time() * 1000)


def get_headers():
    """
    获取请求头
    :return:
    """
    headers = {
        'Connection': 'Keep-Alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-cn',
        'Referer': 'https://plogin.m.jd.com/login/login?appid=300&returnurl=https://wq.jd.com/passport'
                   '/LoginRedirect?state={}&returnurl=https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc'
                   '=&/myJd/home.action&source=wq_passport'.format(get_timestamp()),
        'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_2 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, '
                      'like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5 UCBrowser/13.4.2.1122',
        'Host': 'plogin.m.jd.com'
    }
    return headers


class JDCookies:
    """
    通过扫码登录获取JD Cookies
    """
    def __init__(self):
        self._http = requests.Session()
        self._http.headers = get_headers()

    def __login_entrance(self):
        """
        扫描登录入口，先获取s_token
        :return:
        """
        url = 'https://plogin.m.jd.com/cgi-bin/mm/new_login_entrance?lang=chs&appid=300&returnurl=https://wq.jd.com' \
              '/passport/LoginRedirect?state={}&returnurl=https://home.m.jd.com ' \
              '/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(get_timestamp())
        try:
            response = self._http.get(url)
            return response.json()['s_token']
        except requests.RequestException as e:
            println("获取s_token失败, 原因: {}".format(e.args))

    def __generate_qr_code(self, s_token=''):
        """
        用s_token生成二维码
        :param s_token:
        :return:
        """
        url = 'https://plogin.m.jd.com/cgi-bin/m/tmauthreflogurl?s_token={}&v={}&remember=true'.format(s_token,
                                                                                                       get_timestamp())
        body = 'lang=chs&appid=300&source=wq_passport&returnurl=https://wqlogin2.jd.com/passport/LoginRedirect?state' \
               '={}&returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&' \
               'ufc=&/myJd/home.action'.format(get_timestamp())

        try:
            response = self._http.post(url, body)
            data = response.json()
            token = data['token']
            println(token)
            qr_code_url = 'https://plogin.m.jd.com/cgi-bin/m/tmauth?appid=300&client_type=m&token=' + token

            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=4,
                border=1,
            )
            qr.add_data(qr_code_url)
            qr.make(fit=True)

            println('请扫描二维码登录, 有效期三分钟...', style="bold white")
            try:
                qr.print_ascii(invert=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img.save('./qrcode.png')
                img.show()
            except Exception as e:
                println("显示二维码异常:{}".format(e.args))
                # qr.print_ascii(invert=True)
            println('如二维码不正常, 可使用在线二维码生成工具, 输入以下内容生成二维码:\n{}'.format(qr_code_url))

            return token

        except requests.RequestException as e:
            println("获取二维码失败, 网络异常: {}".format(e.args))

    def __check_login(self, token=''):
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

        println("等待扫码中...", style='bold yellow')
        while True:
            try:
                response = self._http.post(url, body)
                data = response.json()
                if data['errcode'] == 0:
                    pt_pin = self._http.cookies.get('pt_pin')
                    pt_key = self._http.cookies.get('pt_key')
                    println("成功获取cookie, 如下:", style='bold green')
                    println("pt_pin={};pt_key={};".format(pt_pin, pt_key), style='bold green')
                    break
                elif data['errcode'] == 176:  # 等待扫描
                    time.sleep(1)
                else:  # 其他错误
                    println('获取cookies失败, {}!'.format(data['message']))
                    break
            except requests.RequestException as e:
                println("获取登录状态失败, 网络异常...", style='bold red')
                break
            if int(time.time()) - start_time > 60 * 3:
                println("超过三分钟未扫码...", style='bold red')
                break

    def start(self):
        """
        :return:
        """
        println("获取cookie脚本开始执行...", style='bold blue')
        s_token = self.__login_entrance()
        token = self.__generate_qr_code(s_token)
        self.__check_login(token)
        println("获取cookie脚本执行完毕...", style='bold green')
        input("按任意键退出!")


def start():
    jd = JDCookies()
    jd.start()


if __name__ == '__main__':
    start()
