System overview
===============
Certificate issuing
-------------------
The cert-issuer component is responsible for issuing certificates on the blockchain. As described in our Medium post, V1
is using the Bitcoin blockchain.

![Certificate Issuer](/images/cert-issuer.png "Certificate Issuer")


In the current implementation, these 2 tasks are performed by the certificate issuer:
1.	Open badge signature
2.	Issue on blockchain


Because the open badge signature is independent from issuing the certificate as a transaction on the blockchain, this
will likely be pulled out as a separate component in the future.

The input is an unsigned certificate; its schema is described here.

In our implementation, the signing step signs the recipient UID field in the unsigned certificate, and places the
signature in the signature section of the certificate. The signed certificate is retained as output, since the hash of
this document is what it stored on the blockchain.

The next step creates a Bitcoin transaction with the signed certificate hash and outputs to the recipient and the
revocation address.

Cert-issuer’s output is the signed certificate, and the Bitcoin Transaction ID. These two suffice to validate the
certificate.


Certificate viewing, storage, and validation
--------------------------------------------
We provided an additional level of convenience by storing, looking up, and performing validation of the certificates we
issued in a webapp. This is technically optional; with the signed certificate and the Bitcoin transaction id, the
recipient could provide these to any 3rd party they choose, and that 3rd party could independently validate the
certificate. As this project evolves, these different concerns will be pulled into separate components.

![Certificate Viewer](/images/cert-viewer.png "Certificate Viewer")

Lookup and storage requirements will vary according to the sensitivity of the data. In this digital certificate
 scenario, recipients preferred the convenience.

The outputs of the signed certificate and txid suffice to validate the certificate. The means of validating the
certificate are open.



Validation
----------
Validation is clearly a core consideration but I call it out separately because the technique of validating a
certificate is open.

These steps show how you would independently verify a certificate. Note that these steps could have been done without
involving the issuer’s (MIT’s) viewer page:
- The recipient could directly provide the signed certificate and transaction id
- The issuer and revocation keys are available in the bitcoin transaction. The from address is the issuer, and the
revocation address is the output that is not the recipient address (there may also be a change output going back to the
 issuer)


