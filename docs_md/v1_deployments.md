
Findings from our v1 deployments
================================

About
-----
This describes our v1 deployments, their workflows, and usability feedback from both recipients and issuers.

Deployments
-----------

There are two types of workflows in our v1 deployments: recipient-initiated and batch. Here are descriptions of these workflows in practice:

1. Recipient-initiated

	The recipient requests their certificate through a form on the issuer's website. (This form is included in the cert-viewer source). The recipient enters information required for the issuing process, such as their name, cohort/group that is eligible for a certificate, and submits their request. 

	This workflow requires a approval step to weed out invalid requests. In our deployments, in fact, the approval step is performed by someone other than the issuer. To improve this coordination, our deployments used Zapier to export requests from MongoDB to Google sheets. But note that a variety of automated export mechanisms could have been used.

	An approver reviews the sheet at time intervals they choose, toggle a field in the spreadsheet indicating if the certificate should be issued. 

	The issuer monitors for updates to this spreadsheet, then issues the approved certificates, and exports to MongoDB.

    The issuer issues certificates one at a time, or possibly as a batch if several approved requests have queued up.

2. Batch ("cohort")

	In this deployment, the issuer creates a roster of all recipients and their associated data as a batch. For us, the roster was a simple csv file with each recipient's name, certificate details, etc. 

	This workflow doesn't request a separate approval step, since everything in the roster is already approved. So all that's needed is to issue the certificates from the roster and add them to MongoDB.

Automation and current limitations
----------------------------------

The above deployments use scripts that we didn't include in the initial release. We need to consolidate/generalize these scripts and add them to the open source repositories.

These do the following:

- Importing certificates into MongoDB
- Creating certificates from a roster
- Copying unsigned certificates to the issuer

Some steps remain very custom at the moment. For example, the step of creating a new type of certificate involves adding the logo, certificate image, and signature image (all base64-encoded pngs) to the raw json. This is tedious and manual at the moment, but it's only required 1 time per new certificate type; i.e. we script the population of individual recipients' certificates from that template.

Note that a certificate "designer" (i.e. that allows you to upload a logo image) could improve the process of creating a certificate template. 


Recipient Bitcoin address
-------------------------

In one of the deployment types described above, the recipient requests their certificate online. One of the fields we request -- their public Bitcoin address -- has caused a lot of confusion. Some common interpretations/reactions include:

- looks like a freeform field; i.e. I should be make up and enter any identifier I want such as myname123
- pointless/redundant; i.e. why should I have to enter this when I've entered a different identifier like email?

This pointed out that our form lacked Bitcoin address validation, which could have helped catch these issues at request time. But there remains a more fundamental confusion over this field. We had already gotten feedback that
this is a nuisance for the issuer in that they need to wait for input from the recipient. In fact, in the second deployment type we do not request Bitcoin addresses from the user; instead,
we generate Bitcoin addresses on the recipient's behalf and then destroy the private keys<sup>[1](#footnote1)</sup>. This means the recipients cannot revoke the certificate by themselves, and does not allow a strong ownership claim, but was viewed as the best tradeoff for this low stakes certificate.

For context, here is how/why we use the recipient's Bitcoin address. We issue the certificate as a Bitcoin transaction to the recipient. This allows the recipient to revoke their certificate. Note that this address is simply any Bitcoin address the recipient owns. Our approach does not solve the identity problem and, in fact, this allows the recipient flexibility to manage their addresses as they please. For example:

- the recipient can use the same Bitcoin address for all their certificates
- they can use a different Bitcoin address for every certificate, for increased privacy
- they can use an external identity provider and attach certificates

In any case, the recipient's Bitcoin address allows the recipient to make a cryptographically strong ownership claim, as opposed
to claims verified by name, DOB, etc.

In v2 we need to improve this experience. For example a certificate management tool (i.e. "wallet") could help manage and
hide this complexity from the user. We may need to allow the recipient address to be optional in some cases, but the
verification steps would need to reflect this.

Footnotes:

<a name="footnote1">1</a>: We could have attempted to securely transfer the private key to its owner but doing this correctly is incredibly risky. An attempt would look something like this: remaining offline, print each private key to a connected printer (ensuring the printer didn't cache), hand the paper to the recipient. This already is a lot of work, and I've probably left out some exploits in this brief description.
