# Live

These are the steps to issue real certificates on the bitcoin blockchain in our v1 approach.

This is an incubator project, which is not currently intended for release into production, so please use caution whether
you're using as-is or modifying. It's easy to make mistakes with bitcoin transactions and accidentally spend too much!


## Setup

[Using Blockchain.info](blockchain_info.md)

[Using bitcoind](bitcoind.md)


## Additional considerations

In a deployed environment, you'd want to use an additional storage address. You would transfer money from your storage address
to your issuing address before issuing certificates.

As above, you would designate an storage address to store you bitcoin, and transfer a few BTC to this address

Save this address as your `storage_address` in conf.ini, and use the `--transfer_from_storage_address` configuration option.
