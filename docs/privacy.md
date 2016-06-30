Notes on privacy of this approach
=================================
What’s stored on the blockchain is a 1-way hash; you can’t feasibly recover the original data unless:
1. the recipient reveals the original contents, or
2. the issuer maintains an external db with the certificate contents, and lookup is possible.

In our current deployments, we have included capability #2: we copied the certificates to mongodb and indexed them
by certificate uid. We allow cert-viewer to retrieve and display the certificate from a url containing the certificate uid.
Furthermore, we've included "Recently Issued" certificate links on the home page. This sort of disclosure was done only
because the certificates didn't contain sensitive information.

It's crucial to consider the sensitivity of the data before including a capability like #2. For example, if the
certificates we issued contained personal information such as the recipient's address, we would certainly avoid
disclosure via the "Recently Issued" links.

One option that avoids disclosing any information (except when the recipient chooses) is an approach like
https://proofofexistence.com/. In this scheme, verification could work as follows: the recipient reveals the certificate
contents only to whom they choose. Then it can be verified that the certificate hash matches what's on the blockchain.

In general, anticipate the need for a range of solutions balancing convenience, privacy, and security. For example,
a recipient may want it to be easy for 3rd parties to view and verify that they graduated with a B.A. from a university,
but would only want to expose their transcript contents if required.

