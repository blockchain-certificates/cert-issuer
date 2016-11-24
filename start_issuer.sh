#!/usr/bin/env bash
set -x

pid=0

# SIGUSR1-handler
my_handler() {
  echo "my_handler"
}

# SIGTERM-handler
term_handler() {
  if [ $pid -ne 0 ]; then
    kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

# setup handlers
# on callback, kill the last background process, which is `tail -f /dev/null` and execute the specified handler
trap 'kill ${!}; my_handler' SIGUSR1
trap 'kill ${!}; term_handler' SIGTERM

bitcoind -daemon


sleep 3

# create issuing address
issuer=`bitcoin-cli getnewaddress`
sed -i.bak "s/<issuing-address>/$issuer/g" /etc/cert-issuer/conf.ini
bitcoin-cli dumpprivkey $issuer > /etc/cert-issuer/priv.txt

# create revocation address
revocation=`bitcoin-cli getnewaddress`
sed -i.bak "s/<revocation-address>/$revocation/g" /etc/cert-issuer/conf.ini

# make sure you have enough BTC in your issuing address
bitcoin-cli generate 101
bitcoin-cli getbalance
bitcoin-cli sendtoaddress $issuer 5

bitcoin-cli generate 101


sleep 5

bitcoin-cli getreceivedbyaddress $issuer


cd /cert-issuer/
source /cert-issuer/env/bin/activate
export WORK_DIR=/etc/cert-issuer/work
mkdir $WORK_DIR

python service/run.py -c /etc/cert-issuer/conf.ini --usb_name /etc/cert-issuer/ &
pid="$!"

# wait forever
while true
do
  tail -f /dev/null & wait ${!}
done