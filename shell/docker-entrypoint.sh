#!/bin/bash

CODE_DIR='/scripts'

if [ -f "$CODE_DIR/logs/conf.lock" ]; then
    echo "存在配置锁定文件，不执行配置复制操作!"
else
  echo "######初始化配置#####"
  cp $CODE_DIR/conf/.config_example.yaml $CODE_DIR/conf/config.yaml
  cp $CODE_DIR/conf/.crontab.sh $CODE_DIR/conf/crontab.sh
  echo "######添加配置锁定文件######"
  echo "lock" >> $CODE_DIR/logs/conf.lock;
fi


if [ -f "$CODE_DIR/logs/pull.lock" ]; then
  echo "存在更新锁定文件，跳过git pull操作..."
else
  echo "git pull拉取最新代码..."
  cd $CODE_DIR && git pull
  echo "pip install 安装最新依赖"
  pip install -r $CODE_DIR/requirements.txt
  echo "更新脚本配置文件"
  /usr/local/bin/python /scripts/update_config.py
  echo "替換更新文件"
  rm -rf /docker-entrypoint.sh
  cp $CODE_DIR/shell/docker-entrypoint.sh /
  chmod a+x /docker-entrypoint.sh
  echo "重新配置定时任务..."
  crontab -r
  cat $CODE_DIR/shell/default_crontab.sh >> /etc/crontabs/root
  cat $CODE_DIR/conf/crontab.sh >> /etc/crontabs/root
fi


PID=`ps -ef |grep myprocess |grep -v grep | awk '{print $2}'`
if [ "$PID" != "" ]; then
  echo "######定时任务已存在!######"
else
  echo "######启动定时任务######"
  crond -f /etc/crontabs/;
fi