# jd_scripts

## 环境

- python: 3.6+

## 安装

- 进入项目根目录: `cd jd_scripts`.
- 创建虚拟环境: `virtualenv venv`, 如提示命令不存在，则先运行`pip install virtualenv`.
- 激活虚拟环境: `venv/bin/activate`
- 安装项目依赖: `pip install -r requirements.txt`

## 使用

- 获取JD_COOKIES: `python get_jd_cookies.py`, 扫描弹出的二维码进行登录, 控制台会打印JD_COOKIES。

- 设置JD_COOKIES: 
    - linux/mac: `export JD_COOKIES="上面获取到的JD_COOKIES"`, 
      如: `export JD_COOKIES="pt_pin=jd_xxx;pt_key=sadadsfa;"`
      
    - windows: `set JD_COOKIES=上面获取到JD_COOKIES`, 如:`set JD_COOKIES=pt_pin=jd_xxx;pt_key=sadadsfa;`
    
- 执行签到合集: `python jd_sign_collection.py`.