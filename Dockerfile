FROM python:3.8-alpine

ARG CODE_DIR=/jd_scripts

COPY shell/install.sh /

RUN set -ex \
    apk update \
    && apk add --no-cache bash git openssh-client vim gcc python3-dev jpeg-dev zlib-dev musl-dev \
    && ./install.sh $CODE_DIR \
    && rm -rf ./install.sh

WORKDIR $CODE_DIR
exec "$@"
ENTRYPOINT [ "top", "-b" ]

CMD ["/bin/bash"]