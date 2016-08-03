FROM seegno/bitcoind:0.12
MAINTAINER Kim Duffy "kimhd@mit.edu"

# Add bitcoind.conf
RUN mkdir ~/.bitcoin
RUN echo "rpcuser=foo\nrpcpassword=bar\nrpcport=18333\nregtest=1\n" > ~/.bitcoin/bitcoin.conf

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

# Add requirements file.
ADD requirements.txt /cert-issuer/requirements.txt

# Run VirtualEnv.
RUN virtualenv -p /usr/local/bin/python3 /cert-issuer/env/
RUN /cert-issuer/env/bin/pip install wheel

COPY . /cert-issuer

RUN /cert-issuer/env/bin/pip install /cert-issuer/.

# Copy configuration file
RUN mkdir /etc/cert-issuer
COPY conf_regtest.ini /etc/cert-issuer/conf.ini

RUN echo '\ndata_path=/etc/cert-issuer/data\narchive_path=/etc/cert-issuer/archive\n' >> /etc/cert-issuer/conf.ini

COPY ./data /etc/cert-issuer/data
COPY ./archive /etc/cert-issuer/archive



