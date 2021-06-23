#!/bin/bash

cd /jd_scripts;

if [ -f "/scripts/logs/pull.lock" ]; then
  echo "存在更新锁定文件，跳过git pull操作..."
else
  echo "git pull拉取最新代码..."
  git pull
  echo "pip install 安装最新依赖"
  pip install -r requirements.txt
  echo "重新配置定时任务..."
  crontab -r
  cat ./shell/default_crontab.sh >> /etc/crontabs/root
  cat ./config/crontab.sh >> /etc/crontabs/root
  echo "重启crond 服务..."
  pkill -9 crond
  crond -f
fi

