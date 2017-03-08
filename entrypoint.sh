#!/usr/bin/env bash
set -x

source ./exit_handler.sh

ISSUER_CONF=/etc/cert-issuer/conf-common.ini

sleep 1

cd /cert-issuer/

python3 service/run.py -c $ISSUER_CONF &
issuer_pid="$!"
echo "Issuer PID is $issuer_pid"

# setup exit handlers. on callback, kill the last background process, which is `tail -f /dev/null` and execute the specified handler
trap 'kill ${!}; exit_handler ${issuer_pid}' SIGTERM
trap 'kill ${!}; exit_handler ${issuer_pid}' SIGINT

# wait forever
while true
do
  tail -f /dev/null & wait ${!}
done