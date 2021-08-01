# 薅薅乐

- python:3.7+

## 安裝

### 本地运行

- `pip install virtualenv`
- `git clone https://github.com/ClassmateLin/jd_scripts.git`
- `cd jd_scripts`
- `virtualenv venv && source ./venv/bin/activate`
- `pip install -r requirements.txt`
- `mkdir conf && cp .config.yaml ./conf/`

### 使用docker

- docker一键安装: `docker run -d --name jd classmatelin/hhl:latest`, docker-compose配置自行编写, 映射logs和conf目录即可。

## 更新

- `docker exec -it jd /bin/docker-entrypoint`

### 

## 使用

- 进入容器: `docker exec -it jd bash`


- 获取JD_COOKIES: `python get_jd_cookies.py`, 扫描登录成功后控制台会打印JD_COOKIES.

- vim /scripts/conf/config.yaml, 填入上一步获取的JD_COOKIES， `pt_pin=xxx;pt_key=xxx;`和`pt_key=xxx;pt_pin=xxx;`是一样的。

    ```yaml
    debug: true
    
    # JD_COOKIES配置, 一行一个, -符号是必须的。
    jd_cookies: 
      - pt_pin=jd_78b;pt_key=AAJgyqEMOsFQr5a0ucVzJepxU;
    
    # 此处省略更多配置
    ```

- 配置好JD_COOKIES, 随便运行一个脚本检查配置, 如: `python update_share_code.py`.

- 内置定时任务, 配好JD_COOKIES自动会执行脚本。

- 消息通知, 配置config.yaml中的notify块
  - TG机器人: 配置tg_bot_token和tg_user_id
  - PUSH+: 配置push_p_token
  - 企业微信应用消息：配置qywx_am  （依次填上corpid的值,corpsecret的值,touser的值,agentid,media_id的值，注意用,号隔开。）

## 注意
- 脚本都是短短一两个小时写的, 没有经过完全的测试，避免不了有Bug, 如有问题请提issues。

## 脚本列表


| 脚本名称                  | 脚本描述            | 完成进度 |
|:---:|:---:|:---:|
| jd_big_winner.py      | 京东极速版->大赢家翻翻乐 | 100% |
| update_share_code.py  | 更新助力码| 100%|
| jd_bean_change.py      | 资产变动通知 | 100% |
| get_jd_cookies.py     | 获取京东的COOKIES    | 100%      |
| jd_cute_pet.py        | 京东APP->东东萌宠     | 100%        |
| jd_factory.py         | 京东APP->东东工厂     |  100%       |
| jd_farm.py            | 京东APP->东东农场     |  100%       |
| jd_lucky_turntable.py| 幸运大转盘 | 100%  |
| jd_joy.py | 京东APP-> 宠汪汪 | 90% |
| jd_joy_exchange.py | 京东APP-> 宠汪汪 -> 兑换京豆| 100% |
| jd_joy_feed.py | 京东APP-> 宠汪汪 -> 喂狗粮 | 100% |
| jd_planting_bean.py | 京东APP->种豆得豆|  100% |
| jd_ranking_list.py | 京东APP->排行榜 | 100% |
| jd_shark_bean.py | 京东APP->摇京豆 | 100%|
| jd_collar_bean.py | 京东APP->领京豆 | 99%|
| jd_sign_collection.py| 京东签到合集 | 100% |
| jr_daily_task_goose.py| 京东金融->天天提鹅 | 100% |
| jr_pet_pig.py | 京东金融->养猪猪| 100% |
| jr_money_tree.py| 京东金融->摇钱树| 100%|
| jd_bean_lottery.py | 京东APP->签到领京豆->摇京豆->京豆夺宝| 100% |
| jd_earn_bean.py | 微信小程序-赚京豆 | 100% |
| jd_cash.py | 京东APP-领现金 | 100% |
| jd_burning_summer.py | 京东APP-燃动夏季| 100% |
| jd_wishing_pool.py | 京东APP-京东众筹-许愿池| 100% |
| jd_good_morning.py | 京东APP-领京豆->早起福利| 100% |
| jd_bean_home.py | 京东APP-签到领豆->额外京豆/浏览商品| 100% |
| jd_gold_creator.py | 京东APP-京东排行榜->金榜创造营| 100%|
| dj_fruit.py | 京东APP-京东到家->领免费水果| 100%|
| dj_fruit_collect.py | 京东APP-京东到家->领免费水果->点水车| 100%|
| dj_bean.py | 京东APP-京东到家->签到/赚鲜豆| 100%|
| dj_bean_manor.py| 京东APP-京东到家->鲜豆庄园任务| 90%|
| dj_bean_manor_water.py| 京东APP-京东到家->鲜豆庄园->领水/浇水| 100%|
| jd_flash_sale_box.py| 京东APP->品牌闪购->闪购盲盒|100%|
| jd_beauty.py          | 京东APP->美丽研究院   | 0%        |
| jx_factory.py | 京喜APP->京喜工厂 | 0% |
| jx_farm.py | 京喜APP->京喜农场| 0% |
| jd_esports_manager.py | 京东APP->电竞经理     | 0%        |

## 配置说明

- 请查看/scripts/conf/config.yaml中的配置项。


## 特别声明: 

* 本仓库发布的jd_scripts项目中涉及的任何解锁和解密分析脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断.

* 本项目内所有资源文件，禁止任何公众号、自媒体进行任何形式的转载、发布。

* ClassmateLin对任何脚本问题概不负责，包括但不限于由任何脚本错误导致的任何损失或损害.

* 间接使用脚本的任何用户，包括但不限于建立VPS或在某些行为违反国家/地区法律或相关法规的情况下进行传播, ClassmateLin对于由此引起的任何隐私泄漏或其他后果概不负责.

* 请勿将jd_scripts项目的任何内容用于商业或非法目的，否则后果自负.

* 如果任何单位或个人认为该项目的脚本可能涉嫌侵犯其权利，则应及时通知并提供身份证明，所有权证明，本人将在收到认证文件后删除相关脚本.

* 以任何方式查看此项目的人或直接或间接使用该jd_scripts项目的任何脚本的使用者都应仔细阅读此声明。ClassmateLin保留随时更改或补充此免责声明的权利。一旦使用并复制了任何相关脚本或jd_scripts项目的规则，则视为您已接受此免责声明.

**您必须在下载后的24小时内从计算机或手机中完全删除以上内容.**  </br>
***您使用或者复制了本仓库且本人制作的任何脚本，则视为`已接受`此声明，请仔细阅读*** 

