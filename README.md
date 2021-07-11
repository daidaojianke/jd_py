# 薅薅乐

## 安裝

### 使用docker
- docker一键安装: `docker run -d --name jd classmatelin/hhl:latest`.

### 

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


## 脚本列表


| 脚本名称                  | 脚本描述            | 完成进度 |
|:---:|:---:|:---:|
| jd_big_winner.py      | 京东极速版->省钱大赢家翻翻乐 | 100%（活动已过期） |
| update_share_code.py  | 更新助力码, 定时任务每天凌晨自动执行一次| 100%|
| jd_bean_change.py      | 资产变动通知 | 100% |
| get_jd_cookies.py     | 获取京东的COOKIES    | 100%      |
| jd_cute_pet.py        | 京东APP->东东萌宠     | 100%        |
| jd_factory.py         | 京东APP->东东工厂     |  100%       |
| jd_farm.py            | 京东APP->东东农场     |  100%       |
| jd_lucky_turntable.py| 幸运大转盘 | 100%  |
| jd_pet_dog | 京东APP-> 宠汪汪 | 10% |
| jd_planting_bean.py | 京东APP->种豆得豆|  100% |
| jd_ranking_list | 京东APP->排行榜 | 100% |
| jd_shark_bean | 京东APP->摇金豆 | 100%|
| jd_sign_collection| 京东签到合集 | 100% |
| jr_daily_task_goose.py| 京东金融->天天提鹅 | 100% |
| jr_pet_pig | 京东金融->养猪猪| 100% |
| jr_money_tree| 京东金融->摇钱树| 100%|
| jd_bean_lottery.py | 京东APP->签到领京豆->摇金豆->京豆夺宝| 100% |
| jd_earn_bean.py | 微信小程序-赚金豆 | 100% |
| jd_cash.py | 京东APP-领现金 | 100% |
| jd_burning_summer.py | 京东APP-燃动夏季| 95% |
| jd_wishing_pool.py | 京东APP-京东众筹-许愿池| 100% |
| jd_beauty.py          | 京东APP->美丽研究院   | 0%        |
| jx_factory.py | 京喜APP->京喜工厂 | 0% |
| jx_farm.py | 京喜APP->京喜农场| 0% |
| jd_esports_manager.py | 京东APP->电竞经理     | 0%        |


