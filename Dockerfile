FROM seegno/bitcoind:0.13-alpine
MAINTAINER Kim Duffy "kimhd@mit.edu"

COPY . /cert-issuer
COPY conf_regtest.ini /etc/cert-issuer/conf.ini


RUN apk add --update bash python3 \
    && python3 -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip3 install --upgrade pip setuptools \
    && mkdir -p /etc/cert-issuer/work \
    && mkdir -p /etc/cert-issuer/data/unsigned_certificates \
    && mkdir /etc/cert-issuer/data/signed_certificates \
    && mkdir /etc/cert-issuer/data/blockchain_certificates \
    && mkdir ~/.bitcoin \
    && echo $'rpcuser=foo\nrpcpassword=bar\nrpcport=8332\nregtest=1\nrelaypriority=0\nrpcallowip=127.0.0.1\nrpcconnect=127.0.0.1\n' > ~/.bitcoin/bitcoin.conf \
    && pip3 install /cert-issuer/. \
    && apk del py-pip \
    && rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache

ENTRYPOINT bitcoind -daemon && bash
