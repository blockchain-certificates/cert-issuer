---
layout: page
title: Options
---
Reminder: This is an incubator project and is not currently intended for production deployment.

## Cert-issuer docker container

__This is the fastest way to experiment, but is not configured to issue real certificates on the blockchain__


The cert-issuer docker container allows you to experiment with issuing certificates. This uses a bitcoind image, but runs
with the regtest (regression test) flag enabled. This simulates working with the bitcoin blockchain without
actually spending money. This also means that the certificates generated this way are not actually on the bitcoin blockchain.


## Local bitcoind node or Blockchain.info APIs

If you want to issue real certificates, use the local bitcoind or blockchain.info instructions as a starting point.

Because this involves spending money, please use caution and, as always, remember this incubator project is not currently
intended for production release.

 Note that the local bitcoind instance can also be run in regtest mode, to avoid spending money while getting started.

