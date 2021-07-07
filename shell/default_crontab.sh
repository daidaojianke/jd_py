# 默认定时任务

# 京豆夺宝
0 9 * * * /usr/local/bin/python /scripts/jd_bean_indiana.py >> /scripts/logs/jd_bean_indiana.log 2>&1

# 美丽研究院
# 41 7,12,19 * * * /usr/local/bin/python /scripts/jd_beauty.py >> /scripts/logs/jd_beauty.log 2>&1

# 东东萌宠
35 6-18/6 * * * /usr/local/bin/python /scripts/jd_cute_pet.py >> /scripts/logs/jd_cute_pet.log 2>&1

# 赚金豆
# 12 * * * * /usr/local/bin/python /scripts/jd_earn_bean.py >> /scripts/logs/jd_earn_bean.log 2>&1

# 京东电竞经理
# 15 * * * * /usr/local/bin/python /scripts/jd_esports_manager.py >> /scripts/logs/jd_esports_manager.log 2>&1

# 东东工厂
26 * * * * /usr/local/bin/python /scripts/jd_factory.py >> /scripts/logs/jd_factory.log 2>&1

# 东东农场
15 6-18/6 * * * /usr/local/bin/python /scripts/jd_farm.py >> /scripts/logs/jd_farm.log 2>&1

# 抽金豆
6 0 * * * /usr/local/bin/python /scripts/jd_lottery_bean.py >> /scripts/logs/jd_lottery_bean.log 2>&1

# 幸运大转盘
10 10,23 * * * /usr/local/bin/python /scripts/jd_lucky_turntable.py >> /scripts/logs/jd_lucky_turntable.log 2>&1

# 宠汪汪
# 0 1 * * *  /usr/local/bin/python /scripts/jd_joy.py >> /scripts/logs/jd_pet_dog.log 2>&1

# 京东种豆得豆
10 7-22/1 * * * /usr/local/bin/python /scripts/jd_planting_bean.py >> /scripts/logs/jd_planting_bean.log 2>&1

# 京东排行榜
21 9 * * *  /usr/local/bin/python /scripts/jd_ranking_list.py >> /scripts/logs/jd_ranking_list.log 2>&1

# 摇金豆
6 0,23 * * * /usr/local/bin/python /scripts/jd_shark_bean.py >> /scripts/logs/jd_shark_bean.log 2>&1

# 签到合集
7 0,17 * * * /usr/local/bin/python /scripts/jd_sign_collection.py >> /scripts/logs/jd_sign_collection.log 2>&1

# 京东试用
# 0 10 * * *  /usr/local/bin/python /scripts/jd_try.py >> /scripts/logs/jd_try.log 2>&1

# 天天提鹅
28 * * * * /usr/local/bin/python /scripts/jr_daily_take_goose.py >> /scripts/logs/jr_daily_take_goose.log 2>&1

# 金果摇钱树
23 */2 * * * /usr/local/bin/python /scripts/jr_money_tree.py >> /scripts/logs/jr_money_tree.log 2>&1

# 金融养猪
32 0-23/6 * * * /usr/local/bin/python /scripts/jr_pet_pig.py >> /scripts/logs/jr_pet_pig.log 2>&1

# 京喜工厂
# 50 * * * * /usr/local/bin/python /scripts/jx_factory.py >> /scripts/logs/jx_factory.log 2>&1

# 京喜农场
# 30 9,12,18 * * * /usr/local/bin/python /scripts/jx_farm.py >> /scripts/logs/jx_farm.log 2>&1


### 每8小时执行一次更新 ###
0 */8 * * * /docker-entrypoint.sh  >> /dev/null  2>&1