# 薅薅乐

## 安裝

### 使用docker
- docker一键安装: `docker run -d --name jd classmatelin/hhl`.

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
| get_jd_cookies.py     | 获取京东的COOKIES    | 100%      |
| jd_beauty.py          | 京东APP->美丽研究院   | 0%        |
| jd_big_winner.py      | 京东极速版->省钱大赢家翻翻乐 | 100%（活动已过期） |
| jd_cute_pet.py        | 京东APP->东东萌宠     | 0%        |
| jd_esports_manager.py | 京东APP->电竞经理     | 0%        |
| jd_factory.py         | 京东APP->东东工厂     |  0%       |
| jd_farm.py            | 京东APP->东东农场     |  100%       |
| jd_lucky_turntable.py| 幸运大转盘 | 0%  |
| jd_pet_dog | 京东APP-> 宠汪汪 | 0% |
| jd_planting_bean.py | 京东APP->种豆得豆|  100% |
| jd_ranking_list | 京东APP->排行榜 | 100% |
| jd_shark_bean | 京东APP->摇金豆 | 100%|
| jd_sign_collection| 京东签到合集 | 100% |
| jr_daily_task_goose.py| 京东金融->天天提鹅 | 100% |
| jr_pet_pig | 京东金融->养猪猪| 100% |
| jx_factory.py | 京喜APP->京喜工厂 | 0% |
| jx_farm.py | 京喜APP->京喜农场| 0% |
| jd_bean_lottery.py | 京东APP->签到领京豆->摇金豆->京豆夺宝| 100% |


