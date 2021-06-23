### 如需要自定义Crontab，需要在这里写，使用crontab -e写入将会被自动更新程序清除 ###

### 种豆得豆 每天三小时收取一次营养液 ###
0 */3 * * * /usr/bin/python /jd_scripts/jd_planting_bean.py  >> /jd_scripts/logs/jd_planting_bean.log  2>&1