#!/usr/bin/env bash

set -x

function exit_handler {
  issuer_pid=$1

  # kill issuer
  if [ $issuer_pid -ne 0 ]; then
    if [ -e "/proc/${issuer_pid}" ]; then
      echo 'Killing issuer'
      kill -SIGTERM "$issuer_pid"
      wait "$issuer_pid"
    fi
  fi

  exit 143; # 128 + 15 -- SIGTERM
}