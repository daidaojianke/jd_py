# 薅薅乐

## 安裝

- docker一件安装: `docker run -d --name jd classmatelin/hhl`.

## 使用

- 进入容器: `docker exec -it jd bash`

- 获取JD_COOKIES: `python get_jd_cookies.py`, 扫描登录成功后控制台会打印JD_COOKIES.

- vim /jd_scripts/conf/config.yaml, 填入上一步获取的JD_COOKIES。

```yaml
debug: true

# JD_COOKIES配置, 一行一个, -符号是必须的。
jd_cookies: 
  - pt_pin=jd_78b;pt_key=AAJgyqEMOsFQr5a0ucVzJepxU;

# 此处省略更多配置
```

- 配置好JD_COOKIES, 随便运行一个脚本检查配置, 如: `python jd_shark_bean.py`.


## 功能列表

- JD签到合集(41个
- JD种豆得豆
- JD摇金豆
- JD排行榜
- JD极速版翻翻乐
- JD幸运大转盘
- 其他功能开发中...