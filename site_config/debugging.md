---
layout: page
title: Debugging
---

Which client
------------

In general, it was easiest to run bitcoind locally. Running it in regtest mode (without real money) is the safest,
easiest way to experiment with building a bitcoin app. This project's docker container is configured this way.


Bitcoind
--------
###Importing addresses

Addresses must be converted to hash160 to import them. This tool was helpful [http://bitcoinvalued.com/tools.php](http://bitcoinvalued.com/tools.php)

###Creating addresses

Addresses can be created via commandline ```bitcoin-cli getnewaddress```.


Blockchain.info
---------------
Many testing difficulties were related to different functionality in the old/new API, and also the legacy/new wallets available on
the web site. The differences were primarily around the ability to import addresses (more difficult in the new versions). After experimentation, the legacy wallet UI combined with the new API provided all the functionality we needed.

###Creating addresses

We used this client-side generator [http://bitaddress.org/](http://bitaddress.org/)


###Debugging error responses

Each API call and error is logged by cert-issuer. If the error message isn't obvious, it's often easiest to try the
API call that was logged via curl and so you can tweak the call and get answers with faster turnaround.

The most common errors were:

- addresses not belonging to the expected wallet 
- api permissions not being set in the wallet

####Make sure you request 'Create wallet' permissions when getting a Blockchain.info api key
Your api key needs this permission to use cert-issuer. If you messed this up, just request another one.

After you get an api key, open your wallet in the webapp (in legacy format -- reason below), and choose 'enable api
access' in Advanced Settings


####Example Error: "Authorization Required"

> {"initial_error":"Authorization Required. Please check your email."...}
> {"error":"Wallets that require email authorization are currently not supported in the Wallet API. Please disable
> this in your wallet settings, or add the IP address of this server to your wallet IP whitelist."}


Even after enabling API access in your wallet (via the legacy UI), you need to add your IP address to the IP
Whitelist in your wallet. See 'Security > Settings > Advanced Settings > IP Whitelist'.

This was a great error message!

####Example Error: "Address not found in wallet"

cert-issuer needs the ability to spend from issuing address, and from a storage address (if you are using that).

I couldn't find a way to import addresses with the new Blockchain.info wallet and API. This ability was present in
the legacy versions. You can work around this by using the legacy wallet, which allows you to import addresses. On the
'import/export' tab, use 'import private key'

##Looking up transactions

You can validate your transaction before sending by looking it up by rawtx at blockchain.info. Example:

   ```
   curl 'https://blockchain.info/rawtx/45a9306dfe99820eb346bb17ae0b64173ac11cac2d0e4227c7a7cacbcc0bad31?cors=true'
   ```




