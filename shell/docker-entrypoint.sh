#!/bin/bash

CODE_DIR='/jd_scripts'


if [ -f "$CODE_DIR/logs/pull.lock" ]; then
  echo "存在更新锁定文件，跳过git pull操作..."
else
  echo "git pull拉取最新代码..."
  git pull
  echo "pip install 安装最新依赖"
  pip install -r requirements.txt
  echo "替換更新文件"
  rm -rf /docker-entrypoint.sh
  cp $CODE_DIR/shell/docker-entrypoint.sh /
  chmod a+x /docker-entrypoint.sh
  echo "重新配置定时任务..."
  crontab -r
  cat $CODE_DIR/shell/default_crontab.sh >> /etc/crontabs/root
  cat $CODE_DIR/conf/crontab.sh >> /etc/crontabs/root
  echo "重启crond 服务..."
  pkill -9 crond
  crond -f /etc/crontabs/
fi

if [ -f "$CODE_DIR/logs/conf.lock" ]; then
    echo "存在配置锁定文件，不执行配置复制操作!"
else
  echo "######初始化配置#####"
  cp $CODE_DIR/conf/.config_example.yaml $CODE_DIR/conf/config.yaml
  cp $CODE_DIR/conf/.crontab.sh $CODE_DIR/conf/crontab.sh
  echo "######添加配置锁定文件######"
  echo "lock" >> $CODE_DIR/logs/conf.lock
fi