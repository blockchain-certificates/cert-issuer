FROM seegno/bitcoind:0.12
MAINTAINER Kim Duffy "kimhd@mit.edu"

# Add bitcoind.conf
RUN mkdir ~/.bitcoin
RUN echo "rpcuser=foo\nrpcpassword=bar\nrpcport=18333\nregtest=1\n" > ~/.bitcoin/bitcoin.conf

RUN apt-get update

# Install issuer app
RUN apt-get install -y -q build-essential python-gdal python-simplejson --fix-missing
RUN apt-get install -y python python-pip wget
RUN apt-get install -y python-dev

RUN apt-get install -y libssl-dev openssl wget
RUN wget -P /opt/ https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz
RUN tar xzf /opt/Python-3.4.3.tgz -C /opt/

RUN /opt/Python-3.4.3/configure
RUN cd /opt/Python-3.4.3 & make
RUN cd /opt/Python-3.4.3 & make install


# Create a working directory.
RUN mkdir issuer

# Install VirtualEnv.
RUN pip install virtualenv

# Add requirements file.
ADD requirements.txt /issuer/requirements.txt

# Run VirtualEnv.
RUN virtualenv -p /usr/local/bin/python3 /issuer/env/
RUN /issuer/env/bin/pip install wheel

COPY . /issuer

RUN /issuer/env/bin/pip install /issuer/.

# Copy configuration file
RUN mkdir /etc/issuer
COPY conf_regtest.ini /etc/issuer/conf.ini


