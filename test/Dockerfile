FROM centos:8

ENV PIP_REPO="[global]\nindex-url = https://pypi.mirrors.ustc.edu.cn/simple/\n" \
    CODE_DIR=/scripts   \
    REPO_URL=git@gitee.com:ClassmateLin/jd_scripts.git \
    REPO_BRANCH=master \
    PYTHON_DIR=/usr/local/python \
    TEMP_DIR=/tmp/

RUN yum update -y \
    && yum install -y gcc make cmake zlib-devel glibc-langpack-zh bzip2 bzip2-devel readline-devel \
        openssl-devel xz xz-devel libffi-devel cronie wget vim git \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone \
    && export LC_ALL="zh_CN.UTF-8" \
    && wget -P $TEMP_DIR https://www.python.org/ftp/python/3.7.11/Python-3.7.11.tgz \
    && mkdir -p $PYTHON_DIR \
    && cd $TEMP_DIR && tar -zxvf Python-3.7.11.tgz && cd Python-3.7.11 \
    && ./configure --prefix=$PYTHON_DIR && make && make install \
    && ln -s $PYTHON_DIR/bin/python3  /usr/bin/python \
    && ln -s $PYTHON_DIR/bin/pip3 /usr/bin/pip \
    && echo "export PATH=$PATH:"$PYTHON_DIR"/bin" >> /etc/profile && source /etc/profile \
    && mkdir -p /root/.pip && echo -e $PIP_REPO > /root/.pip/pip.conf \
    && rm -rf ~/.cache/pip \
    && yum clean all \
    && rm -rf /var/lib/yum/yumdb \
    && rm -rf $TEMP_DIR/Python-3.7.11.tgz


