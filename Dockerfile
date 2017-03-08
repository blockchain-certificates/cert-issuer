FROM seegno/bitcoind:0.13-alpine
MAINTAINER Kim Duffy "kimhd@mit.edu"

COPY . /cert-issuer
COPY conf-common.ini /etc/cert-issuer/conf-common.ini
COPY priv.txt /etc/cert-issuer/priv.txt
COPY priv2.txt /etc/cert-issuer/priv2.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY exit_handler.sh /exit_handler.sh

RUN apk add --update bash python python3 ca-certificates \
    && pip3 install --upgrade pip \
    && mkdir /etc/cert-issuer/work \
    && mkdir /etc/cert-issuer/data \
    && pip3 install /cert-issuer/. \
    && apk del py-pip \
    && rm -rf /var/cache/apk/*

ENTRYPOINT ["/entrypoint.sh"]
