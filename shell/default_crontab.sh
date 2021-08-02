# 默认定时任务

SHELL=/bin/sh

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# 定时更新脚本
30 15 * * * /bin/docker-entrypoint >> /dev/null  2>&1

# 每2个小时检查一次cookies是否过期
0 */2 * * * /scripts/check_cookies.py >> /scripts/logs/check_cookies_`date "+\%Y-\%m-\%d"`.log 2>&1

### 更新助力码
3 0,16 * * * /scripts/update_share_code.py >> /scripts/logs/update_share_code_`date "+\%Y-\%m-\%d"`.log 2>&1

 #  京东到家 签到赚鲜豆
45 7,12,19 * * * /scripts/dj_bean.py >> /scripts/logs/dj_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东到家->鲜豆庄园
30 6,21 * * * /scripts/dj_bean_manor.py >> /scripts/logs/dj_bean_manor_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东到家鲜豆庄园领水浇水
*/40 * * * * /scripts/dj_bean_manor_water.py >> /scripts/logs/dj_bean_manor_water_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->京东到家->领免费水果
10 7,11,18 * * * /scripts/dj_fruit.py >> /scripts/logs/dj_fruit_`date "+\%Y-\%m-\%d"`.log 2>&1

#  到家果园收水滴
42 */1 * * * /scripts/dj_fruit_collect.py >> /scripts/logs/dj_fruit_collect_`date "+\%Y-\%m-\%d"`.log 2>&1

#  资产变动通知
15 */8 * * * /scripts/jd_bean_change.py >> /scripts/logs/jd_bean_change_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->我的->签到领京豆->领额外奖励
45 0 * * * /scripts/jd_bean_home.py >> /scripts/logs/jd_bean_home_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京豆APP->摇京豆->豆夺宝
10 9 * * * /scripts/jd_bean_indiana.py >> /scripts/logs/jd_bean_indiana_`date "+\%Y-\%m-\%d"`.log 2>&1

#  省钱大赢家翻翻乐
3 */1 * * * /scripts/jd_big_winner.py >> /scripts/logs/jd_big_winner_`date "+\%Y-\%m-\%d"`.log 2>&1

#  签到领现金
46 */12 * * * /scripts/jd_cash.py >> /scripts/logs/jd_cash_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->领京豆
6 1 * * * /scripts/jd_collar_bean.py >> /scripts/logs/jd_collar_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->我的->东东萌宠
35 6-18/6 * * * /scripts/jd_cute_pet.py >> /scripts/logs/jd_cute_pet_`date "+\%Y-\%m-\%d"`.log 2>&1

#  赚京豆(微信小程序)-赚京豆-签到领京豆
45 5,22 * * * /scripts/jd_earn_bean.py >> /scripts/logs/jd_earn_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->东东工厂
30 6-18/6 * * * /scripts/jd_factory.py >> /scripts/logs/jd_factory_`date "+\%Y-\%m-\%d"`.log 2>&1

#  东东工厂收电量
10 */1 * * * /scripts/jd_factory_collect.py >> /scripts/logs/jd_factory_collect_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP-东东农场
15 6-18/6 * * * /scripts/jd_farm.py >> /scripts/logs/jd_farm_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP闪购盲盒
15 5,23 * * * /scripts/jd_flash_sale_box.py >> /scripts/logs/jd_flash_sale_box_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->排行榜->金榜创造营
30 7,19 * * * /scripts/jd_gold_creator.py >> /scripts/logs/jd_gold_creator_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP早起福利
30 6 * * * /scripts/jd_good_morning.py >> /scripts/logs/jd_good_morning_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->我的->宠汪汪
45 8,12,17 * * * /scripts/jd_joy.py >> /scripts/logs/jd_joy_`date "+\%Y-\%m-\%d"`.log 2>&1

#  宠汪汪商品兑换
56 7,15,23 * * * /scripts/jd_joy_exchange.py >> /scripts/logs/jd_joy_exchange_`date "+\%Y-\%m-\%d"`.log 2>&1

#  宠汪汪喂狗
10 */3 * * * /scripts/jd_joy_feed.py >> /scripts/logs/jd_joy_feed_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->签到领京豆->抽京豆
6 0 * * * /scripts/jd_lottery_bean.py >> /scripts/logs/jd_lottery_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

#  幸运大转盘
10 10,23 * * * /scripts/jd_lucky_turntable.py >> /scripts/logs/jd_lucky_turntable_`date "+\%Y-\%m-\%d"`.log 2>&1

#  种豆得豆
10 3,15 * * * /scripts/jd_planting_bean.py >> /scripts/logs/jd_planting_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

# 
40 */2 * * * /scripts/jd_planting_bean_collect.py >> /scripts/logs/jd_planting_bean_collect_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东排行榜
21 9 * * * /scripts/jd_ranking_list.py >> /scripts/logs/jd_ranking_list_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->我的->签到领豆->摇京豆
6 0,18,23 * * * /scripts/jd_shark_bean.py >> /scripts/logs/jd_shark_bean_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东签到合集
7 0,17 * * * /scripts/jd_sign_collection.py >> /scripts/logs/jd_sign_collection_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东APP->每日特价->疯狂砸金蛋
45 5,19 * * * /scripts/jd_smash_golden_egg.py >> /scripts/logs/jd_smash_golden_egg_`date "+\%Y-\%m-\%d"`.log 2>&1

#  众筹许愿池,
45 */12 * * * /scripts/jd_wishing_pool.py >> /scripts/logs/jd_wishing_pool_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东金融APP->天天提鹅
35 9,22 * * * /scripts/jr_daily_take_goose.py >> /scripts/logs/jr_daily_take_goose_`date "+\%Y-\%m-\%d"`.log 2>&1

#  天天提额收鹅蛋
5 */1 * * * /scripts/jr_daily_take_goose_collect.py >> /scripts/logs/jr_daily_take_goose_collect_`date "+\%Y-\%m-\%d"`.log 2>&1

#  金果摇钱树
5 10,21 * * * /scripts/jr_money_tree.py >> /scripts/logs/jr_money_tree_`date "+\%Y-\%m-\%d"`.log 2>&1

#  摇钱树收金果
35  */1 * * * /scripts/jr_money_tree_collect.py >> /scripts/logs/jr_money_tree_collect_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京东金融->养猪猪
23 0-23/8 * * * /scripts/jr_pet_pig.py >> /scripts/logs/jr_pet_pig_`date "+\%Y-\%m-\%d"`.log 2>&1

#  京喜App->惊喜工厂
38 7,12,18 * * * /scripts/jx_factory.py >> /scripts/logs/jx_factory_`date "+\%Y-\%m-\%d"`.log 2>&1

