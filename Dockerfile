FROM python:3.8-alpine

WORKDIR /

COPY shell/install.sh .

RUN set -ex \
    apk update \
    && apk add --no-cache bash git openssh-client vim gcc python3-dev jpeg-dev zlib-dev musl-dev \
    && ./install.sh \
    && rm -rf ./install.sh

CMD ["/bin/bash"]