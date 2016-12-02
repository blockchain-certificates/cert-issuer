FROM seegno/bitcoind:0.13-alpine
MAINTAINER Kim Duffy "kimhd@mit.edu"

COPY . /cert-issuer
COPY conf_regtest_common.ini /etc/cert-issuer/conf_regtest_common.ini
COPY conf_testnet_common.ini /etc/cert-issuer/conf_testnet_common.ini
COPY bitcoin-regtest.conf /etc/cert-issuer/bitcoin-regtest.conf
COPY bitcoin-testnet.conf /etc/cert-issuer/bitcoin-testnet.conf
COPY priv.txt /etc/cert-issuer/priv.txt
COPY entrypoint-regtest.sh /entrypoint-regtest.sh
COPY entrypoint-testnet.sh /entrypoint-testnet.sh

RUN apk add --update bash python python3 py-pip \
    && pip3 install --upgrade pip \
    && mkdir /etc/cert-issuer/work \
    && mkdir /etc/cert-issuer/data \
    && mkdir ~/.bitcoin \
    && pip3 install /cert-issuer/. \
    && apk del py-pip \
    && rm -rf /var/cache/apk/* \
    && chmod +x /entrypoint-regtest.sh \
    && chmod +x /entrypoint-testnet.sh

ENTRYPOINT ["/entrypoint-testnet.sh", "/entrypoint-regtest.sh"]
