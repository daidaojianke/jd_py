FROM python:3.7-alpine

COPY ./shell/install.sh /tmp/

RUN set -ex \
    apk update \
    && apk add --no-cache bash git openssh-client vim gcc jpeg-dev zlib-dev musl-dev tzdata libffi-dev \
    && echo "Asia/Shanghai" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && /tmp/install.sh /jd_scripts \
    && rm -rf /tmp/install.sh

WORKDIR /jd_scripts

ENTRYPOINT [ "/docker-entrypoint.sh"]

CMD ["/bin/bash"]