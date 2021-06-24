#!/bin/bash

cd /jd_scripts;

if [ -f "/scripts/logs/pull.lock" ]; then
  echo "存在更新锁定文件，跳过git pull操作..."
else
  echo "修复时区错误";
  apk add tzdata;
  echo "Asia/Shanghai" > /etc/timezone;
  ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime;
  echo "git pull拉取最新代码..."
  git pull
  echo "pip install 安装最新依赖"
  pip install -r requirements.txt
  echo "替換更新文件"
  rm -rf /docker-entrypoint.sh
  cp ./shell/docker-entrypoint.sh /
  chmod a+x /docker-entrypoint.sh
  echo "重新配置定时任务..."
  crontab -r
  cat ./shell/default_crontab.sh >> /etc/crontabs/root
  cat ./conf/crontab.sh >> /etc/crontabs/root
  echo "重启crond 服务..."
  pkill -9 crond
  crond -f /etc/crontabs/
fi

