FROM ubuntu:18.04
maintainer kim duffy "kimhd@mit.edu"
maintainer yancy ribbens "yribbens@credly.com"

RUN apt-get update -qq && apt-get install -y git wget build-essential libtool autotools-dev automake pkg-config libssl-dev libevent-dev bsdmainutils python3 libboost-all-dev libminiupnpc-dev libzmq3-dev libqt5gui5 libqt5core5a libqt5dbus5 qttools5-dev qttools5-dev-tools libprotobuf-dev protobuf-compiler libqrencode-dev

# Checkout bitcoin source
RUN mkdir /bitcoin-source
WORKDIR /bitcoin-source
RUN git clone https://github.com/bitcoin/bitcoin.git

# Install Berkley Database
RUN wget http://download.oracle.com/berkeley-db/db-4.8.30.NC.tar.gz
RUN tar -xvf db-4.8.30.NC.tar.gz
WORKDIR /bitcoin-source/db-4.8.30.NC/build_unix
RUN mkdir -p build
RUN BDB_PREFIX=$(pwd)/build
RUN ../dist/configure --disable-shared --enable-cxx --with-pic --prefix=$BDB_PREFIX
RUN make install

# install bitcoin 0.16.3
WORKDIR /bitcoin-source/bitcoin
RUN ./autogen.sh
RUN ./configure CPPFLAGS="-I${BDB_PREFIX}/include/ -O2" LDFLAGS="-L${BDB_PREFIX}/lib/" --with-gui
RUN make
RUN make install
