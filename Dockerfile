FROM python:3.7.11-slim-buster

COPY ./requirements.txt ./docker-entrypoint.sh /root/

RUN apt update -y \
    && apt install -y bash vim cron git \
    && chsh -s /bin/bash \
    && echo Asia/Shanghai > /etc/timezone && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && export LC_ALL="C.UTF-8" \
    && mkdir -p /root/.ssh /root/.pip \
    && ssh-keyscan github.com > /root/.ssh/known_hosts \
    && bash -c "echo -e '[global]\nindex-url = https://pypi.mirrors.ustc.edu.cn/simple/\n' > /root/.pip/pip.conf" \
    && pip install -U pip --no-cache-dir && pip install -r /root/requirements.txt --no-cache-dir \
    && chmod a+x /root/docker-entrypoint.sh && mv /root/docker-entrypoint.sh /bin/docker-entrypoint \
    && apt clean && rm -rf /root/.cache/pip && rm -rf /root/requirements.txt

ENTRYPOINT ["/bin/docker-entrypoint"]

CMD ["/bin/bash"]