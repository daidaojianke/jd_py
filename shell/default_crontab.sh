# 默认定时任务

# 京豆夺宝
0 9 * * * /scripts/jd_bean_indiana.py >> /scripts/logs/jd_bean_indiana_`date "+\%Y-\%m-\%d"`.log 2>&1

# 美丽研究院
41 7,12,19 * * * /scripts/jd_beauty.py >> /scripts/logs/jd_beauty_`date "+\%Y-\%m-\%d"`.log 2>&1

# 东东萌宠
35 6-18/6 * * * /scripts/jd_cute_pet.py >> /scripts/logs/jd_cute_pet_`date "+\%Y-\%m-\%d"`.log 2>&1

# 赚金豆
12 * * * * /scripts/jd_earn_bean.py >> /scripts/logs/jd_earn_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 京东电竞经理
15 * * * * /scripts/jd_esports_manager.py >> /scripts/logs/jd_esports_manager_`date "+\%Y-\%m-\%d"`.log 2>&1

# 东东工厂
26 * * * * /scripts/jd_factory.py >> /scripts/logs/jd_factory_`date "+\%Y-\%m-\%d"`.log 2>&1

# 东东农场
15 6-18/6 * * * /scripts/jd_farm.py >> /scripts/logs/jd_farm_`date "+\%Y-\%m-\%d"`.log 2>&1

# 抽金豆
6 0 * * * /scripts/jd_lottery_bean.py >> /scripts/logs/jd_lottery_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 领金豆
6 1 * * * /scripts/jd_collar_bean.py >> /scripts/logs/jd_collar_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 幸运大转盘
10 10,23 * * * /scripts/jd_lucky_turntable.py >> /scripts/logs/jd_lucky_turntable_`date "+\%Y-\%m-\%d"`.log 2>&1

# 宠汪汪做任务
45 8,12,17  * * *  /scripts/jd_joy.py >> /scripts/logs/jd_pet_dog_`date "+\%Y-\%m-\%d"`.log 2>&1

# 宠汪汪兑换京豆
58 7,15,23 * * * /scripts/jd_joy_exchange.py >> /scripts/logs/jd_joy_exchange_`date "+\%Y-\%m-\%d"`.log 2>&1

# 宠汪汪喂狗每三小时喂一次
35 */3 * * * /scripts/jd_joy_feed.py >> /scripts/logs/jd_joy_feed_`date "+\%Y-\%m-\%d"`.log 2>&1

# 京东种豆得豆
10 7-22/1 * * * /scripts/jd_planting_bean.py >> /scripts/logs/jd_planting_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 京东排行榜
21 9 * * *  /scripts/jd_ranking_list.py >> /scripts/logs/jd_ranking_list_`date "+\%Y-\%m-\%d"`.log 2>&1

# 摇金豆
6 0,18,23 * * * /scripts/jd_shark_bean.py >> /scripts/logs/jd_shark_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 签到合集
7 0,17 * * * /scripts/jd_sign_collection.py >> /scripts/logs/jd_sign_collection_`date "+\%Y-\%m-\%d"`.log 2>&1

# 京东试用
0 10 * * *  /scripts/jd_try.py >> /scripts/logs/jd_try_`date "+\%Y-\%m-\%d"`.log 2>&1

# 天天提鹅
28 * * * * /scripts/jr_daily_take_goose.py >> /scripts/logs/jr_daily_take_goose_`date "+\%Y-\%m-\%d"`.log 2>&1

# 金果摇钱树
23 */2 * * * /scripts/jr_money_tree.py >> /scripts/logs/jr_money_tree_`date "+\%Y-\%m-\%d"`.log 2>&1

# 金融养猪
32 0-23/6 * * * /scripts/jr_pet_pig.py >> /scripts/logs/jr_pet_pig_`date "+\%Y-\%m-\%d"`.log 2>&1

# 京喜工厂
50 * * * * /scripts/jx_factory.py >> /scripts/logs/jx_factory_`date "+\%Y-\%m-\%d"`.log 2>&1

# 京喜农场
30 9,12,18 * * * /scripts/jx_farm.py >> /scripts/logs/jx_farm_`date "+\%Y-\%m-\%d"`.log 2>&1

# 微信小程序-赚京豆
15 5,15 * * * /scripts/jd_earn_bean.py >> /scripts/logs/jd_earn_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 资产变动通知
30 9,13,19,23 * * * /scripts/jd_bean_change.py >> /scripts/logs/jd_bean_change_`date "+\%Y-\%m-\%d"`.log 2>&1

# 签到领现金
46 8,12,16 * * * /scripts/jd_cash.py >> /scripts/logs/jd_cash_`date "+\%Y-\%m-\%d"`.log 2>&1

# 燃动夏季
30 7,15,19 * * * /scripts/jd_burning_summer.py >> /scripts/logs/jd_burning_summer_`date "+\%Y-\%m-\%d"`.log 2>&1

# 众筹许愿池
45 8,10,14,16,18 * * * /scripts/jd_wishing_pool.py >> /scripts/logs/jd_wishing_pool_`date "+\%Y-\%m-\%d"`.log 2>&1

# 早起福利
30 0,6 * * * /scripts/jd_good_morning.py >> /scripts/logs/jd_good_morning_`date "+\%Y-\%m-\%d"`.log 2>&1

# 金榜创造营
30 7,19 * * * /scripts/jd_gold_creator.py >> /scripts/logs/jd_gold_creator_`date "+\%Y-\%m-\%d"`.log 2>&1

# 疯狂砸金蛋
30 7,19 * * * /scripts/jd_smash_golden_egg.py >> /scripts/logs/jd_smash_golden_egg_`date "+\%Y-\%m-\%d"`.log 2>&1

# 翻翻乐
30 * * * * /scripts/jd_big_winner.py >> /scripts/logs/jd_big_winner_`date "+\%Y-\%m-\%d"`.log 2>&1

# 到家果园
10 7,11,18 * * * /scripts/dj_fruit.py >> /scripts/logs/dj_fruit_`date "+\%Y-\%m-\%d"`.log 2>&1

# 到家果园领水滴
35 */1 * * * /scripts/dj_fruit_collect.py >> /scripts/logs/dj_fruit_collect_`date "+\%Y-\%m-\%d"`.log 2>&1

# 京东到家赚鲜豆
45 12,19 * * * /scripts/dj_bean.py >> /scripts/logs/dj_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 每天23:30清除前一天日志
30 23 * * * /scripts/clean_log.py

# 每2个小时检查一次cookies是否过期
0 */2 * * * /scripts/check_cookies.py >> /scripts/logs/check_cookies_`date "+\%Y-\%m-\%d"`.log 2>&1

### 每天15点30分执行一次更新
30 15 * * * /bin/docker-entrypoint >> /dev/null  2>&1