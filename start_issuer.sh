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
source /cert-issuer/env/bin/activate
cd /cert-issuer/
python service/run.py -c conf_testnet_common.ini --usb_name /cert-issuer/ &
pid="$!"

# wait forever
while true
do
  tail -f /dev/null & wait ${!}
done