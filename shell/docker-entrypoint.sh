#!/bin/bash
echo "######开始执行更新脚本######"

if [ -z $CODE_DIR ]; then
  CODE_DIR=/scripts
fi

if [ -z $REPO_URL ]; then
  REPO_URL=https://github.com/ClassmateLin/jd_scripts.git
fi

if [ ! -d $CODE_DIR/.git ]; then
  echo "代码目录为空, 开始clone代码..."
  cd $CODE_DIR;
  git init;
  git branch -M master;
  git remote add origin $REPO_URL;
  git pull origin master;
  git branch --set-upstream-to=origin/master master;
fi

if [ ! -d $CODE_DIR/conf ]; then
  echo "配置文件目录不存在, 创建目录..."
  mkdir -p $CODE_DIR/conf
fi

if [ ! -d $CODE_DIR/logs ]; then
  echo "日志目录不存在, 创建目录..."
  mkdir -p $CODE_DIR/conf
fi

if [ -f "$CODE_DIR/conf/config.yaml" ]; then
    echo "配置文件已存在, 跳过..."
else
  echo "配置文件不存在, 复制配置文件..."
  cp $CODE_DIR/.config.yaml $CODE_DIR/conf/config.yaml
  cp $CODE_DIR/.crontab.sh $CODE_DIR/conf/crontab.sh
fi

echo "git pull拉取最新代码..."
cd $CODE_DIR && git pull
echo "pip install 安装最新依赖..."
pip install -r $CODE_DIR/requirements.txt
echo "更新docker-entrypoint..."
cp $CODE_DIR/shell/docker-entrypoint.sh /bin/docker-entrypoint
chmod a+x /bin/docker-entrypoint

echo "更新cron任务..."
crontab -r
cat $CODE_DIR/shell/default_crontab.sh >> /var/spool/cron/crontabs/root
echo -e "\n" >> /var/spool/cron/crontabs/root
cat $CODE_DIR/conf/crontab.sh >> /var/spool/cron/crontabs/root
echo "重启cron进程..."
/etc/init.d/cron restart

echo "######更新脚本执行完毕######"

# 保证容器不退出
tail -f /dev/null