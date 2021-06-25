###  签到合集, 每天00:00和16:00执行 ###
0 */16 * * * /usr/local/bin/python /jd_scripts/jd_sign_collection.py  >> /jd_scripts/logs/jd_sign_collection.log  2>&1

### 大赢家翻翻乐 每小时翻一次 ###
0 */1 * * *  /usr/local/bin/python /jd_scripts/jd_big_winner.py  >> /jd_scripts/logs/jd_big_winner.log  2>&1

### 幸运大转盘 每天00:01执行 ###
1 0 * * * /usr/local/bin/python /jd_scripts/jd_lucky_turntable.py  >> /jd_scripts/logs/jd_lucky_turntable.log  2>&1

### 摇京豆 每天00:02执行 ###
2 0 * * * /usr/local/bin/python /jd_scripts/jd_shark_bean.py  >> /jd_scripts/logs/jd_shark_bean.log  2>&1

### 天天提鹅 每天30分钟执行 ###
*/30 * * * * /usr/local/bin/python /jd_scripts/jd_shark_bean.py  >> /jd_scripts/logs/jd_shark_bean.log  2>&1

### 种豆得豆 每天三十分钟执行一次 ###

*30 0 * * * /usr/local/bin/python /jd_scripts/jd_planting_bean.py  >> /jd_scripts/logs/jd_planting_bean.log  2>&1

### 京东排行榜 每天00:04执行 ###
4 0 * * * /usr/local/bin/python /jd_scripts/jd_ranking_list.py  >> /jd_scripts/logs/jd_ranking_list.log  2>&1

### 每8小时执行一次更新 ###
0 */8 * * * /docker-entrypoint.sh  >> /dev/null  2>&1