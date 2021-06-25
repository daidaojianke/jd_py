FROM python:3.8-alpine

COPY ./shell/install.sh /tmp/

RUN set -ex \
    apk update \
    && apk add --no-cache bash git openssh-client vim gcc python3-dev jpeg-dev zlib-dev musl-dev tzdata \
    && echo "Asia/Shanghai" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && /tmp/install.sh /jd_scripts \
    && rm -rf /tmp/install.sh

WORKDIR /jd_scripts

ENTRYPOINT [ "/docker-entrypoint.sh"]

CMD ["/bin/bash"]