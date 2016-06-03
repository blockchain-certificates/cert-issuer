About cert-issuer's Bitcoin transactions
========================================

Exactly what are the transaction outputs?
-----------------------------------------

The current approach creates 1 transaction per certificate recipient. A transaction's outputs are:

- 1 output to the recipient's address, dust amount
- 1 output to the revocation address, dust amount
- Optionally change to the issuer address
- OP_RETURN field, storing 1-way hash of the signed certificate

The OP_RETURN field is the most important w.r.t certificates on the blockchain. This is the field that we use to store
the hash, and in turn we can look it up on the blockchain at any time to validate.

This field was introduced because bitcoin core developers to address ([but not necessarily endorse](https://en.bitcoin.it/wiki/OP_RETURN)) the increasing desire
 of people to store non-financial transactions on the blockchain. OP_RETURN signifies that an output is provably
  unspendable, allowing transactions to be pruned from the UXTO database.

Note that our additional transaction outputs complicate this. One of the other outputs has a very small amount of money going to the recipient’s address, and the other has a same
 amount going to the issuer’s revocation address. The latter is a convention we introduced to enable revocation.


What is dust?
-------------

It is the minimum amount a transaction output can be. I found the best description in
[this Stack Overflow thread](http://bitcoin.stackexchange.com/questions/10986/what-is-meant-by-bitcoin-dust). See
especially Murch’s statements:

```
A transaction output is considered dust when the cost of spending it is close to its value.
Precisely, Bitcoin Core defines dust to be an output whose fees exceed 1/3 of its value. This computes to everything
 smaller than 546 satoshis being considered dust by Bitcoin Core
 ...
It is defined as 546 satoshis in the code.
```

How did you come up with the tx fee?
------------------------------------

We used the current value of 'To get in next block' of [Recommended Bitcoin Network Transaction Fees](http://bitcoinexchangerate.org/fees)

Other resources that were helpful in creating raw bitcoin transactions and computing fees
-----------------------------------------------------------------------------------------
- [Calculating transaction size](http://bitcoin.stackexchange.com/questions/1195/how-to-calculate-transaction-size-before-sending/3011#3011)
- [Creating raw transactions](https://www.reddit.com/r/Bitcoin/comments/2zdwr0/how_do_i_create_a_raw_transaction/)
- [Creating raw transactions](http://www.righto.com/2014/02/bitcoins-hard-way-using-raw-bitcoin.html)
- [Dust limit](https://www.reddit.com/r/Bitcoin/comments/2unzen/what_is_bitcoins_dust_limit_precisely/)


