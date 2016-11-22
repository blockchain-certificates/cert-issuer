FROM seegno/bitcoind:0.12
MAINTAINER Kim Duffy "kimhd@mit.edu"

# Add bitcoind.conf
RUN mkdir ~/.bitcoin

#RUN echo "rpcuser=foo\nrpcpassword=bar\nrpcport=8332\ntestnet=1\nserver=1\nrpctimeout=30\n" > ~/.bitcoin/bitcoin.conf

RUN echo "rpcuser=foo\nrpcpassword=bar\nrpcport=8332\nregtest=1\nrelaypriority=0\nrpcallowip=127.0.0.1\nrpcconnect=127.0.0.1\n" > ~/.bitcoin/bitcoin.conf


RUN apt-get update

# Install cert-issuer app
RUN apt-get install -y -q build-essential
RUN apt-get install -y python python-pip wget
RUN apt-get install -y python-dev

RUN apt-get install -y libssl-dev openssl wget
RUN wget -P /opt/ https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
RUN tar xzf /opt/Python-3.4.3.tgz -C /opt/

RUN /opt/Python-3.4.3/configure
RUN cd /opt/Python-3.4.3 & make
RUN cd /opt/Python-3.4.3 & make install

# Create a working directory.
RUN mkdir cert-issuer

# Install VirtualEnv.
RUN pip install virtualenv

COPY . /cert-issuer

# Create and set up the virtualenv
RUN virtualenv -p /usr/local/bin/python3 /cert-issuer/env/

RUN chmod +x /cert-issuer/env/bin/activate

RUN /bin/bash -c "source /cert-issuer/env/bin/activate && pip install /cert-issuer/."

# Active this virtualenv when the container run interactively
RUN echo "source /cert-issuer/env/bin/activate" >> /root/.bashrc

# Copy configuration file
RUN mkdir /etc/cert-issuer
COPY conf_regtest_common.ini /etc/cert-issuer/conf.ini

COPY start_issuer.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
