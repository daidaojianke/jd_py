# jd_scripts

## 环境

- python: 3.8

## 安装

- 创建并进入文件夹: `mkdir jd && cd jd` 

- 运行容器: `docker run -itd -v config.yaml:/jd_scripts/conf/config.yaml -v logs:/jd_scripts/logs --name jd classmatelin:scripts`

## 配置

- 配置文件: `config.yaml`.

- JD_COOKIES配置, 在配置文件中修改jd_cookies选项, 一行一个jd_cookie, 例如:

```yaml
# 以上省略其他配置

jd_cookies:
  - pt_pin=jd_1;pt_key=AAJgwFk;   # 账号1
  - pt_pin=jd_2;pt_key=AAJgwFk;   # 账号2

# 以下省略其他配置
```

## 手动运行脚本

进入容器: `docker exec -it jd bash`

- 获取JD COOKIES: `python get_jd_cookies.py`.

- 执行签到脚本: `python jd_sign_collection.py`
