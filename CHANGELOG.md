# CHANGELOG



## v3.6.0 (2024-03-07)

### Chore

* chore(SemanticRelease): install twine ([`555dd16`](https://github.com/blockchain-certificates/cert-issuer/commit/555dd16b460e1fc9d7307e07e6dd1c534165d15d))

* chore(SemanticRelease): use release_package as build_command, as recommended by the migration doc

https://python-semantic-release.readthedocs.io/en/latest/migrating_from_v7.html#repurposing-of-version-and-publish-commands ([`d02caed`](https://github.com/blockchain-certificates/cert-issuer/commit/d02caed7a071e2604cc3ca9c8dae3d6f1ec2340d))

* chore(SemanticRelease): run only on merge build ([`d26ee30`](https://github.com/blockchain-certificates/cert-issuer/commit/d26ee30d30bff3d960bd65cd3fc3299bd050ea1a))

* chore(SemanticRelease): revert to v7 with support for pypi uplaod ([`0f2fc9a`](https://github.com/blockchain-certificates/cert-issuer/commit/0f2fc9a34513940ed8ed788e4a27a3ed5fb68c37))

* chore(SemanticRelease): specify upload to pypi - maybe ([`f2e4a30`](https://github.com/blockchain-certificates/cert-issuer/commit/f2e4a30fe273152ee1fb85bd737451d62b7d3706))

* chore(SemanticRelease): specify where version is defined ([`3293630`](https://github.com/blockchain-certificates/cert-issuer/commit/3293630b2db2a88e124c74d87041fff59fd39c92))

* chore(SemanticRelease): add build_command ([`dd266f1`](https://github.com/blockchain-certificates/cert-issuer/commit/dd266f16ed4290cdbe1cb6c84d1e9d5040685f0e))

* chore(SemanticRelease): add semantic-release config ([`70c8114`](https://github.com/blockchain-certificates/cert-issuer/commit/70c81149ee2d4f30eb4102aa485ceaeda43e2fa4))

* chore(SemanticRelease): run version before publish ([`4b8e5ac`](https://github.com/blockchain-certificates/cert-issuer/commit/4b8e5ac673d72532f02a6f88cf8809e6a3bac60e))

* chore(CI): debug git and semantic release ([`8478dc9`](https://github.com/blockchain-certificates/cert-issuer/commit/8478dc9fdc13a66f4d63f4dca8a2e1dd8d0eeb5c))

* chore(CI): only trigger build when merged ([`0eb4362`](https://github.com/blockchain-certificates/cert-issuer/commit/0eb4362869947c1db167695a2f2acee2fc34581c))

* chore(CI): re-enable semantic release publish ([`7ad9fd5`](https://github.com/blockchain-certificates/cert-issuer/commit/7ad9fd5a6458f133656ab4f5c1ed5bd094727737))

* chore(Compliance): update compliance status ([`3ed92a0`](https://github.com/blockchain-certificates/cert-issuer/commit/3ed92a049e8ac020ff2008e80106c8a2186e6d5f))

* chore(deps): bump get-func-name from 2.0.0 to 2.0.2

Bumps [get-func-name](https://github.com/chaijs/get-func-name) from 2.0.0 to 2.0.2.
- [Release notes](https://github.com/chaijs/get-func-name/releases)
- [Commits](https://github.com/chaijs/get-func-name/commits/v2.0.2)

---
updated-dependencies:
- dependency-name: get-func-name
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`0383454`](https://github.com/blockchain-certificates/cert-issuer/commit/0383454152de92ad8a5db4d30c967dc6c5a4b032))

* chore(deps): bump semver from 5.7.1 to 5.7.2

Bumps [semver](https://github.com/npm/node-semver) from 5.7.1 to 5.7.2.
- [Release notes](https://github.com/npm/node-semver/releases)
- [Changelog](https://github.com/npm/node-semver/blob/v5.7.2/CHANGELOG.md)
- [Commits](https://github.com/npm/node-semver/compare/v5.7.1...v5.7.2)

---
updated-dependencies:
- dependency-name: semver
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt; ([`18f78a6`](https://github.com/blockchain-certificates/cert-issuer/commit/18f78a6ed19dbf56343264b0fae12076f2ee679f))

### Feature

* feat(CredentialSubject): compare credential subject against credential schema before issuance ([`2618b20`](https://github.com/blockchain-certificates/cert-issuer/commit/2618b20752d2a1da8c40f0e8fe8488083223fc12))

* feat(CredentialSchema): verify credentialSchema property validity ([`77d219b`](https://github.com/blockchain-certificates/cert-issuer/commit/77d219b5437a20ade67ea4343931fa39420f6738))

* feat(DataIntegrityProof): handle contexts for data integrity proof ([`b13182b`](https://github.com/blockchain-certificates/cert-issuer/commit/b13182b6b6b8a07b529f986a2caa11ed177a93ef))

* feat(DataIntegrityProof): handle chained proofs according to DataIntegrityProof spec ([`601a216`](https://github.com/blockchain-certificates/cert-issuer/commit/601a2168ab6b3bc00f73fb58266748d5940c43a6))

* feat(DataIntegrityProof): add id to proof ([`814cede`](https://github.com/blockchain-certificates/cert-issuer/commit/814cede6ef80d6c4e9be417eb2e879431ef92353))

* feat(DataIntegrityProof): convert proof format to data integrity proof ([`5f9215e`](https://github.com/blockchain-certificates/cert-issuer/commit/5f9215ea769f9f54541089286dc67f7bd330679d))

* feat(Vc-V2): bump deeps ([`0c83ef1`](https://github.com/blockchain-certificates/cert-issuer/commit/0c83ef1d74b1df660c24e4a6817cbeeec6ff7081))

* feat(Vc-V2): verify expirationDate/validUntil is set after issuanceDate/validFrom ([`eaf47c8`](https://github.com/blockchain-certificates/cert-issuer/commit/eaf47c8a4f5f320516f329964f2b23716bb4348f))

* feat(Vc-V2): add validFrom/validUntil verification ([`cb41e73`](https://github.com/blockchain-certificates/cert-issuer/commit/cb41e73831e36f1edfe8da91932571072bac4914))

* feat(Vc-V2): prevent having both v1 and v2 vc context defined ([`f46dffa`](https://github.com/blockchain-certificates/cert-issuer/commit/f46dffac072c20d5a925aec2ce56210eb63429ca))

* feat(Vc-V2): allow VC v2 context in cert ([`d942606`](https://github.com/blockchain-certificates/cert-issuer/commit/d9426063d7c5781ec14f6926023838ae04f1dd49))

* feat(Vc-V2): bump cert-schema ([`c70f0b5`](https://github.com/blockchain-certificates/cert-issuer/commit/c70f0b553f8d2c825b7852c1a52135d61d5a8002))

### Fix

* fix(Deps): remove unused dependency ([`94d3f83`](https://github.com/blockchain-certificates/cert-issuer/commit/94d3f839f6ee2581f95aaded7bd47e7c838209df))

### Refactor

* refactor(DataIntegrityProof): remove chainedProof2021 class ([`96c6abe`](https://github.com/blockchain-certificates/cert-issuer/commit/96c6abe1a4dbb8e4471598057a0403e70f0df664))

* refactor(DataIntegrityProof): move responsibility of creating proof object to proof handler ([`4b20423`](https://github.com/blockchain-certificates/cert-issuer/commit/4b20423afc257881c4e1ca84a8e1b87d61820dba))

* refactor(DataIntegrityProof): extract merkle proof 2019 to its own constructor ([`889440b`](https://github.com/blockchain-certificates/cert-issuer/commit/889440b7c2fc605861d46325da14401682db901b))

### Unknown

* Merge pull request #278 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): install twine ([`03f398d`](https://github.com/blockchain-certificates/cert-issuer/commit/03f398d265d3d6cc433a3212cee03c8d865d34c1))

* Merge pull request #277 from blockchain-certificates/chore/fix-semantic-release

Chore/fix semantic release ([`3ce03fd`](https://github.com/blockchain-certificates/cert-issuer/commit/3ce03fd7cc06609d494193bf3923ba2d44e788eb))

* Revert &#34;chore(SemanticRelease): revert to v7 with support for pypi uplaod&#34;

This reverts commit 0f2fc9a34513940ed8ed788e4a27a3ed5fb68c37. ([`c701a12`](https://github.com/blockchain-certificates/cert-issuer/commit/c701a12de13c7aaad0124bb80c2b9e4edeb975bc))

* Revert &#34;chore(SemanticRelease): run only on merge build&#34;

This reverts commit d26ee30d30bff3d960bd65cd3fc3299bd050ea1a. ([`897de72`](https://github.com/blockchain-certificates/cert-issuer/commit/897de7237c660ae06fe6c2ea3fc082f51a20104a))

* Merge pull request #276 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): run only on merge build ([`18cfd3f`](https://github.com/blockchain-certificates/cert-issuer/commit/18cfd3f9cbf3d405b24ad37445e496c5768a7e25))

* Merge pull request #275 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): revert to v7 with support for pypi uplaod ([`ac5e13d`](https://github.com/blockchain-certificates/cert-issuer/commit/ac5e13da7eb6f1f8d04d8429bf9d83a9c35e003e))

* Merge pull request #274 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): specify upload to pypi - maybe ([`b8b35a7`](https://github.com/blockchain-certificates/cert-issuer/commit/b8b35a7900a0e121f56f5e43dc479d92f0a75682))

* Merge pull request #273 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): specify where version is defined ([`837f5d6`](https://github.com/blockchain-certificates/cert-issuer/commit/837f5d6add2d484dc0302ce141096dce95729336))

* Merge pull request #272 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): add build_command ([`a4f2eb6`](https://github.com/blockchain-certificates/cert-issuer/commit/a4f2eb65afdf5984260dc827287ce14afa88a99a))

* Merge pull request #271 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): add semantic-release config ([`597fe5f`](https://github.com/blockchain-certificates/cert-issuer/commit/597fe5f4bcf0c17ad1b67005a94f2962f56a0453))

* Merge pull request #270 from blockchain-certificates/feat/support-credential-schema

chore(SemanticRelease): run version before publish ([`c0e2738`](https://github.com/blockchain-certificates/cert-issuer/commit/c0e2738f415c1f333412888eef7a67c761116d44))

* Merge pull request #269 from blockchain-certificates/feat/support-credential-schema

chore(CI): re-enable semantic release publish ([`8d0b7c2`](https://github.com/blockchain-certificates/cert-issuer/commit/8d0b7c2ba6e07a48dc1cc4e4747c717bf76bb572))

* Merge pull request #268 from blockchain-certificates/feat/support-credential-schema

Feat/support credential schema ([`efc311d`](https://github.com/blockchain-certificates/cert-issuer/commit/efc311d1cebbf1583e285c896cac253b013cc011))

* Merge pull request #266 from blockchain-certificates/feat/follow-data-integrity-proof

Feat/follow data integrity proof ([`71adf6c`](https://github.com/blockchain-certificates/cert-issuer/commit/71adf6ceecbed3c2dc785665cc4dcbd2a5ff5277))

* Merge branch &#39;master&#39; of https://github.com/blockchain-certificates/cert-issuer into feat/follow-data-integrity-proof ([`3dc65ff`](https://github.com/blockchain-certificates/cert-issuer/commit/3dc65ffc4258e57323fbe191c761f4e1dc4db9e0))

* Merge pull request #265 from blockchain-certificates/feat/vc-v2-validFrom-validUntil

Feat/vc v2 valid from valid until ([`19a2fc3`](https://github.com/blockchain-certificates/cert-issuer/commit/19a2fc3e43dd1d7a8fa41ff00e37ee7bc98dcd0c))

* Merge pull request #263 from blockchain-certificates/dependabot/npm_and_yarn/get-func-name-2.0.2

chore(deps): bump get-func-name from 2.0.0 to 2.0.2 ([`41c4550`](https://github.com/blockchain-certificates/cert-issuer/commit/41c45500587dbdbc32c590552fe1af23082bd582))

* Merge pull request #264 from blockchain-certificates/fix/update-deps

fix(Deps): remove unused dependency ([`6df70eb`](https://github.com/blockchain-certificates/cert-issuer/commit/6df70eb2fb3b971f1618911a72e7044e115c9757))

* Merge pull request #258 from blockchain-certificates/dependabot/npm_and_yarn/semver-5.7.2

chore(deps): bump semver from 5.7.1 to 5.7.2 ([`d8d36f5`](https://github.com/blockchain-certificates/cert-issuer/commit/d8d36f5e207dee130ed2e08858b2f80ab919d992))


## v3.5.0 (2023-06-07)

### Chore

* chore(Compliance): update compliance status ([`acfd4b7`](https://github.com/blockchain-certificates/cert-issuer/commit/acfd4b73cda3d766daf2087bc91aef65a310d7d2))

* chore(CI): revert run on PR branch ([`65f4150`](https://github.com/blockchain-certificates/cert-issuer/commit/65f4150ee5b3bbb2001e426fb290ce542d4b6503))

* chore(Compliance): publish compliance report on blockcerts.org ([`4506058`](https://github.com/blockchain-certificates/cert-issuer/commit/450605860f7d7fdad5faa91399a6b247c94cc81c))

* chore(Compliance): run publish report only on PR ([`5d83c48`](https://github.com/blockchain-certificates/cert-issuer/commit/5d83c48675dfbf7e34c8fc5e160af5610bc61221))

### Unknown

* Merge pull request #256 from blockchain-certificates/feat/multiple-signatures-non-chained

Support non chained signatures ([`b4d939e`](https://github.com/blockchain-certificates/cert-issuer/commit/b4d939e9a3546bd1e762be17b7a71831aaeb77ad))

* Revert &#34;feat(ConcurrentProofs): chain sign concurrent proofs with merkle root of previous proofs&#34;

This reverts commit 8449a9bc8798ce29759e5c1ba95d1919b0ae9a64. ([`1ecd92f`](https://github.com/blockchain-certificates/cert-issuer/commit/1ecd92f5b895ba2f4f6ad9570ae85b41b46d40b7))

* Merge branch &#39;master&#39; of https://github.com/blockchain-certificates/cert-issuer into feat/concurrent-signatures ([`3461408`](https://github.com/blockchain-certificates/cert-issuer/commit/3461408df9556405683c0d3fc4674a871c61e095))

* Merge pull request #255 from blockchain-certificates/test/vc-compliance

chore(Compliance): publish compliance report on blockcerts.org ([`45dd96c`](https://github.com/blockchain-certificates/cert-issuer/commit/45dd96c7e6e86070257a41b4b7231eed4860f2b1))

* Merge pull request #254 from blockchain-certificates/test/vc-compliance

chore(Compliance): run publish report only on PR ([`9fde14f`](https://github.com/blockchain-certificates/cert-issuer/commit/9fde14fe9e85b1d74f3105444617b8571e351166))


## v3.4.0 (2023-05-26)

### Chore

* chore(Compliance): run publish only on PR ([`1413e52`](https://github.com/blockchain-certificates/cert-issuer/commit/1413e52e5cdbf8992e3c7df8ff1163861ac40e07))

* chore(CI): only build master ([`8941ab6`](https://github.com/blockchain-certificates/cert-issuer/commit/8941ab6f7bd5cb019a77a9e4fec71515010365d9))

* chore(CI): only run on master branch ([`65d50b3`](https://github.com/blockchain-certificates/cert-issuer/commit/65d50b3949189faf84624c552d4ad49578ceb996))

* chore(Compliance): update compliance report ([`3b3eeee`](https://github.com/blockchain-certificates/cert-issuer/commit/3b3eeee67ade61ac2c96ab735653eda4a3cfefdc))

* chore(CI): fix typo ([`102bad4`](https://github.com/blockchain-certificates/cert-issuer/commit/102bad40e0ad8cbee9f5a3854d15ac5253380aa8))

* chore(CI): fix typo ([`8e79505`](https://github.com/blockchain-certificates/cert-issuer/commit/8e795050647972a2c1e727972455e67825ff5b56))

* chore(CI): debug CI ([`1e4acae`](https://github.com/blockchain-certificates/cert-issuer/commit/1e4acae1f72c1d11b4b27438687129199c3b011c))

* chore(CI): debug CI ([`369592c`](https://github.com/blockchain-certificates/cert-issuer/commit/369592cb5a5fc189f5783725f8261871d6a3c25c))

* chore(CI): debug CI ([`621fb1a`](https://github.com/blockchain-certificates/cert-issuer/commit/621fb1a67beda9ff9e45b58942344df085083532))

* chore(Compliance): update compliance report ([`fbd8f67`](https://github.com/blockchain-certificates/cert-issuer/commit/fbd8f67ca0c4e32472b578f92b62be0f56accd3b))

* chore(Compliance): fix badge color ([`9ae1083`](https://github.com/blockchain-certificates/cert-issuer/commit/9ae1083a5adc96c39f1a43b858de98d49a758552))

* chore(Compliance): only run on master branch ([`12fb64a`](https://github.com/blockchain-certificates/cert-issuer/commit/12fb64ae84b3508050e673197ae5810ac6d860a7))

* chore(Compliance): update compliance report ([`c231ed8`](https://github.com/blockchain-certificates/cert-issuer/commit/c231ed8920ef581fb7d8b7c4285318079210b8f0))

* chore(Compliance): update first line of README with latest badge status ([`55b34b8`](https://github.com/blockchain-certificates/cert-issuer/commit/55b34b875691f533bd4ad4ce87ee197bf43dc81a))

* chore(Compliance): create badge and populate readme with status (tentative) ([`13c58c7`](https://github.com/blockchain-certificates/cert-issuer/commit/13c58c768ca64c2b119255e04eeeb6ca94038912))

* chore(Compliance): only run report update on master branch. Ignore compliance private key ([`0e951cd`](https://github.com/blockchain-certificates/cert-issuer/commit/0e951cd2b80914e8f1d77c6f8d3c1901a2337045))

* chore(Compliance): update compliance report ([`8f3e111`](https://github.com/blockchain-certificates/cert-issuer/commit/8f3e11176b26fdde57b1aa1cb623cbd382a2854d))

* chore(Compliance): match target head ([`1a1a4fd`](https://github.com/blockchain-certificates/cert-issuer/commit/1a1a4fd38944d326fe23039660222ad498dcc7c9))

* chore(Compliance): debug commit content ([`e8115d4`](https://github.com/blockchain-certificates/cert-issuer/commit/e8115d47f13d8f054e308e377641ff41956b7554))

* chore(Compliance): attempt Github auth ([`e1f8959`](https://github.com/blockchain-certificates/cert-issuer/commit/e1f8959e48a9401b49f075f1445a75a59b5046ca))

* chore(CI): debug ([`28f5824`](https://github.com/blockchain-certificates/cert-issuer/commit/28f58241f228715a9d817ba66d9c32075f444589))

* chore(Compliance): dwbug CI ([`c2f5e16`](https://github.com/blockchain-certificates/cert-issuer/commit/c2f5e16d29c60d84217accc9b69bb2a2f3a7df7f))

* chore(Compliance): copy report file and commit to repo ([`bc268ca`](https://github.com/blockchain-certificates/cert-issuer/commit/bc268caf59bd7e29bf68a56d828d44e8d5ce4d31))

* chore(Compliance): bump version ([`927c5a0`](https://github.com/blockchain-certificates/cert-issuer/commit/927c5a0064b78a0c86ec87a71d5619416db7dbeb))

* chore(compliance): bump version ([`22ecf45`](https://github.com/blockchain-certificates/cert-issuer/commit/22ecf4585dbd6354bc3880f1e2835c160df7a996))

* chore(Compliance): bump version ([`ae46d7f`](https://github.com/blockchain-certificates/cert-issuer/commit/ae46d7f60fa64334a2006993d7a9ffdce2854bcc))

### Feature

* feat(StatusList): support issuance of array credentialStatus property value ([`71cabce`](https://github.com/blockchain-certificates/cert-issuer/commit/71cabce20191dc5b56279c00adcc7831fd89ca1f))

* feat(ConcurrentProofs): chain sign concurrent proofs with merkle root of previous proofs ([`8449a9b`](https://github.com/blockchain-certificates/cert-issuer/commit/8449a9bc8798ce29759e5c1ba95d1919b0ae9a64))

* feat(ConcurrentProofs): allow setting nature of multiple proofs by config/CLI ([`6ebf7f1`](https://github.com/blockchain-certificates/cert-issuer/commit/6ebf7f142105d5373d356cdce2d3be33310a2041))

* feat(ProofHandler): add concurrent proof ([`8670875`](https://github.com/blockchain-certificates/cert-issuer/commit/867087522e20774aa8f2301ec89808207a544c2b))

### Refactor

* refactor(ProofHandler): add chained flag ([`29f91bb`](https://github.com/blockchain-certificates/cert-issuer/commit/29f91bb2a6cf3786c0e026f13c96b4a593fe9f15))

### Unknown

* Merge pull request #251 from blockchain-certificates/test/vc-compliance

Test/vc compliance ([`9133b17`](https://github.com/blockchain-certificates/cert-issuer/commit/9133b17b42053efd91b768547caa9fed22f70ad2))

* Merge branch &#39;test/vc-compliance&#39; of https://github.com/blockchain-certificates/cert-issuer into test/vc-compliance ([`368f1b0`](https://github.com/blockchain-certificates/cert-issuer/commit/368f1b0ae17045fc99c2270d4080d3af178c624a))

* Merge branch &#39;test/vc-compliance&#39; of https://github.com/blockchain-certificates/cert-issuer into test/vc-compliance ([`434334c`](https://github.com/blockchain-certificates/cert-issuer/commit/434334ce9bab8a33cbf7bd19248b34b9b4b039fe))

* Merge branch &#39;test/vc-compliance&#39; of https://github.com/blockchain-certificates/cert-issuer into test/vc-compliance ([`810350e`](https://github.com/blockchain-certificates/cert-issuer/commit/810350e073df6deaded20e45f602f1343f91de2b))

* Merge branch &#39;test/vc-compliance&#39; of https://github.com/blockchain-certificates/cert-issuer into test/vc-compliance ([`5c67a2a`](https://github.com/blockchain-certificates/cert-issuer/commit/5c67a2a35ceddc17431544be3c3c89b7228dac92))

* Merge pull request #239 from digit-ink/master

Enable EIP-1559 ETH txs and update deprecated web3 methods/packages ([`48420fa`](https://github.com/blockchain-certificates/cert-issuer/commit/48420face863658f9412472ce2ce8e823b345581))

* Merge pull request #253 from blockchain-certificates/feat/status-list-2021

feat(StatusList): support issuance of array credentialStatus property… ([`a34a9ac`](https://github.com/blockchain-certificates/cert-issuer/commit/a34a9acefd24b38ddd324530e548a1ea47949f0c))

* Merge pull request #248 from dallarosa/dallarosa-fix-dockerfile-regtest

fix Dockerfile ([`2414aa2`](https://github.com/blockchain-certificates/cert-issuer/commit/2414aa2758148b32a4cedcee702d14c58b7bce14))

* fix Dockerfile

Added the header [regtest] to bitcoin.conf, fixing the error:
&#34;Error: Config setting for -rpcport only applied on regtest network when in [regtest] section.&#34; ([`c528638`](https://github.com/blockchain-certificates/cert-issuer/commit/c5286388d9bc09ebec4e9119323f8dc0c55f00ce))


## v3.3.0 (2022-08-25)

### Chore

* chore(CI): enable semantic release for real ([`ed3d51b`](https://github.com/blockchain-certificates/cert-issuer/commit/ed3d51b72a0c361e739ddaee9c5c9c8fc41f2039))

* chore(CI): configure semantic release to pick up version from tag ([`1e2873f`](https://github.com/blockchain-certificates/cert-issuer/commit/1e2873f7b76cc991c635869948df2cc5906c62b7))

* chore(CI): configure git user ([`5b6c0be`](https://github.com/blockchain-certificates/cert-issuer/commit/5b6c0bef3ac1f5b9f500b811361390c06729e609))

* chore(CI): add debug verbosity ([`ac99779`](https://github.com/blockchain-certificates/cert-issuer/commit/ac99779fb802866641aa93d133b31a8d15d52b95))

* chore(CI): dry-mode for CI configuration ([`6ba2337`](https://github.com/blockchain-certificates/cert-issuer/commit/6ba2337c56ff6710d71a9b14411e4f41e5398a3c))

* chore(SemanticRelease): revert version to 0.0.0 ([`a953103`](https://github.com/blockchain-certificates/cert-issuer/commit/a953103f10bdca2cd3b78bea3e161a5044bc827c))

* chore(CI): break line ([`ae8e823`](https://github.com/blockchain-certificates/cert-issuer/commit/ae8e8231756cc8933f61dfa79a1bb97d88520fb1))

* chore(CI): configure semantic-release ([`9fe0781`](https://github.com/blockchain-certificates/cert-issuer/commit/9fe078189a287a53825268f0ab286f652be65737))

* chore(version): bump version and update dependencies ([`a643fff`](https://github.com/blockchain-certificates/cert-issuer/commit/a643fff114acbb29f2575710a5277e1925cc8a15))

### Documentation

* docs(GoerliAndSepolia): update docs about new supported Ethereum testnets, goerli and sepolia. ([`0355520`](https://github.com/blockchain-certificates/cert-issuer/commit/035552091c469279eca40725e49b6d53c6aae3f1))

### Feature

* feat(GoerliAndSepolia): support Ethereum testnets, goerli and sepolia. ([`a7c3834`](https://github.com/blockchain-certificates/cert-issuer/commit/a7c38345496e1398d097c05751ae72190a297233))

### Refactor

* refactor(GoerliAndSepolia): make it simple using chain.is_bitcoin_type(), is_mock_type(), and is_ethereum_type() ([`fd8785d`](https://github.com/blockchain-certificates/cert-issuer/commit/fd8785d534b7c4178827e0aff6bf5c8907a5c595))

### Unknown

* Merge pull request #245 from blockchain-certificates/chore/semantic-release

chore(CI): enable semantic release for real ([`3d07ec8`](https://github.com/blockchain-certificates/cert-issuer/commit/3d07ec8997aadc9639a02789d841e8d1250cac29))

* Merge pull request #244 from blockchain-certificates/chore/semantic-release

chore(CI): configure semantic release to pick up version from tag ([`3dd6aa8`](https://github.com/blockchain-certificates/cert-issuer/commit/3dd6aa8a3539b321f8863304308f27a75632b052))

* Merge pull request #243 from blockchain-certificates/chore/semantic-release

chore(CI): configure git user ([`ebc4b99`](https://github.com/blockchain-certificates/cert-issuer/commit/ebc4b998279e4a4c76a4bcd4b368db5f8ac7e18a))

* Merge pull request #242 from blockchain-certificates/chore/semantic-release

chore(CI): add debug verbosity ([`d97d5be`](https://github.com/blockchain-certificates/cert-issuer/commit/d97d5be190007bc535a879fb69e4092a6c0de48e))

* Merge pull request #241 from blockchain-certificates/chore/semantic-release

chore(CI): dry-mode for CI configuration ([`66aa531`](https://github.com/blockchain-certificates/cert-issuer/commit/66aa531d22c9f60a8dae5d4ad7ba6ad6de9c660b))

* Merge pull request #240 from blockchain-certificates/chore/semantic-release

chore(CI): configure semantic-release ([`3915889`](https://github.com/blockchain-certificates/cert-issuer/commit/3915889e830f3e607b558589587194edd3c8b98c))

* update UnableToSignTxError() and delete redundant variable ([`107cd83`](https://github.com/blockchain-certificates/cert-issuer/commit/107cd83e9f7e55333673b1cadcee66771f1b0669))

* Enable EIP-1559-compliant ETH transactions and update deprecated web3 methods/packages ([`4f293b3`](https://github.com/blockchain-certificates/cert-issuer/commit/4f293b351127e1e0d791a1d7a44f1a582a90feaa))

* Merge pull request #237 from koshilife/support-goerli-and-sepolia

Support Ethereum testnets, the Goerli and the Sepolia ([`323601a`](https://github.com/blockchain-certificates/cert-issuer/commit/323601a50e5fe111ea03054eef60bebc651a86ec))


## v3.2.0 (2022-07-12)

### Chore

* chore(Package): bump version ([`f7b3543`](https://github.com/blockchain-certificates/cert-issuer/commit/f7b3543d25819aa4706bf7bbafbbf00e8ab293a2))

* chore(MultiSign): ignore context dir ([`adb447e`](https://github.com/blockchain-certificates/cert-issuer/commit/adb447eb81dfb6e362170cc0dbeee5c96962e214))

* chore(MultiSign): do not maintain context in git repo ([`c0478ed`](https://github.com/blockchain-certificates/cert-issuer/commit/c0478ed2a83084ab7dc12103fdaf849b0dc29cd5))

* chore(Release): update release package script ([`55a850a`](https://github.com/blockchain-certificates/cert-issuer/commit/55a850ab5444d10baf57d16591f621355cf9ebdc))

### Documentation

* docs(MultiSign): update readme ([`41eb02d`](https://github.com/blockchain-certificates/cert-issuer/commit/41eb02d1e72f1acee8eb5c2df2518db19174817f))

* docs(v3): update examples ([`cb7b880`](https://github.com/blockchain-certificates/cert-issuer/commit/cb7b8800a8559239703443bd50b0338a2291d33f))

* docs(V3): update documentation ([`7ce5a0a`](https://github.com/blockchain-certificates/cert-issuer/commit/7ce5a0a0bb5eae9f6871f8fd22747342b51a7e01))

* docs(Issuer): update id ([`926d996`](https://github.com/blockchain-certificates/cert-issuer/commit/926d996ec4cdf739d0f5da909938832c99f9673d))

* docs(Issuer): add fixed github URLs ([`f8ca6b9`](https://github.com/blockchain-certificates/cert-issuer/commit/f8ca6b9d13f74936c48476b897b6ae933df2547b))

* docs(Issuer): add sample issuer details ([`06477d0`](https://github.com/blockchain-certificates/cert-issuer/commit/06477d083d0c7a0bcfa1e4480f51242be3977400))

### Feature

* feat(Metadata): check if title property is defined ([`265df12`](https://github.com/blockchain-certificates/cert-issuer/commit/265df1277d8af41430459aeee66faeccdad28c40))

* feat(Metadata): verify metadata when validating certificate ([`fa3fa7e`](https://github.com/blockchain-certificates/cert-issuer/commit/fa3fa7ea207ce3f84a87409521af6ed71e7bb1db))

* feat(Metadata): only warn once when group is not defined ([`53b5e2c`](https://github.com/blockchain-certificates/cert-issuer/commit/53b5e2ccb2bd752a252c5d1aa472f9cf8f116b4a))

* feat(Metadata): check properties existence as defined from display order ([`03b39aa`](https://github.com/blockchain-certificates/cert-issuer/commit/03b39aaedc42bec0afc1aaed9a44873f10afba18))

* feat(Metadata): add metadata json schema validation ([`748985e`](https://github.com/blockchain-certificates/cert-issuer/commit/748985e0939e85bf2636048de775ddba648a47b4))

* feat(MultiSign): allow passing multiple contexts through command line param ([`0f0a3be`](https://github.com/blockchain-certificates/cert-issuer/commit/0f0a3be84576caf46a54dbdf2cefec85ecff1fd5))

* feat(MultiSign): allow passing one context through command line param ([`fb6f1ba`](https://github.com/blockchain-certificates/cert-issuer/commit/fb6f1ba2128c730075a9b15565b637e5f4f189f0))

* feat(MultiSign): register context before issuance ([`d7e1a6b`](https://github.com/blockchain-certificates/cert-issuer/commit/d7e1a6b2a215479d4d25485dcd9f490aec675e97))

* feat(MultiSign): bump version ([`ce82385`](https://github.com/blockchain-certificates/cert-issuer/commit/ce82385c335fc0876b408ce72e5f3bd89b49b584))

* feat(MultiSign): add merkle proof context if document is v3.1 ([`64530ad`](https://github.com/blockchain-certificates/cert-issuer/commit/64530ad44b3325340d9be8faff066b8d98a7eb15))

* feat(MultiSign): update context to reflect signature suites ([`9f75673`](https://github.com/blockchain-certificates/cert-issuer/commit/9f75673584645693192377cc35f77bbe06464bb4))

* feat(MultiSign): bump cert-schema ([`f23cc57`](https://github.com/blockchain-certificates/cert-issuer/commit/f23cc5767fb873edf2302bbd924a05df6b02f365))

* feat(MultiSign): allow n amount of proofs to be chained ([`1c6e3b4`](https://github.com/blockchain-certificates/cert-issuer/commit/1c6e3b4ad8cecc429afddd03a0fb1a9b09687d62))

* feat(V3): provide check to make sure blockcerts context is last ([`18e5396`](https://github.com/blockchain-certificates/cert-issuer/commit/18e539661f04a8f7e9462eb16d7f5eb2bae1979b))

* feat(v3): bump cert-schema dependency ([`8aa3290`](https://github.com/blockchain-certificates/cert-issuer/commit/8aa3290af3d8b79d806d252734efeeae69c2e677))

* feat(v3): bump cert-schema dependency ([`2bdf62d`](https://github.com/blockchain-certificates/cert-issuer/commit/2bdf62d5a744d1f7a3e58ea30a471daebbe99736))

* feat(v3): prepare version ([`34c30dc`](https://github.com/blockchain-certificates/cert-issuer/commit/34c30dc75b7e1ada7fd093f932b875b3e2846cd0))

* feat(Schema): bump cert-schema ([`8b7a1b9`](https://github.com/blockchain-certificates/cert-issuer/commit/8b7a1b96ecd9854d33543bab7cae4035783caa90))

### Fix

* fix(RFC3339): fix regex to differentiate closing group Z or timezone offset ([`41f1797`](https://github.com/blockchain-certificates/cert-issuer/commit/41f1797f6152052d785da16e20837c05abc1cfb1))

* fix(ChainedProof2021): deep copy previous proof to prevent modification by reference ([`0a67cc6`](https://github.com/blockchain-certificates/cert-issuer/commit/0a67cc67c4252a2a9e635092810c602b5b3cb38e))

* fix(Date): allow more valid RFC3339 string values ([`ad7c0b2`](https://github.com/blockchain-certificates/cert-issuer/commit/ad7c0b28ccf3f384bf50acee77f1ca3e96875cd3))

* fix(Context): limit valid context addresses according to cert-schema preloading ([`67693ad`](https://github.com/blockchain-certificates/cert-issuer/commit/67693ad61cfc347af925cc2c6097a15a025aa0f8))

* fix(v3): ensure display is properly hashed ([`f1b1af4`](https://github.com/blockchain-certificates/cert-issuer/commit/f1b1af43ac44906cbe8afa5e1632cf225d488485))

* fix(Etherscan): [#205] prevent captcha request when calling Etherscan ropsten api ([`2998dd6`](https://github.com/blockchain-certificates/cert-issuer/commit/2998dd6a1693ef49c930948a20f00dbf79fdb3ef))

### Refactor

* refactor(Models): split models file for sanity of the man ([`54bb61a`](https://github.com/blockchain-certificates/cert-issuer/commit/54bb61a552b08162bfec98b44da89082e899a956))

* refactor(JSONLD): centralize jsonld handler ([`f8022b0`](https://github.com/blockchain-certificates/cert-issuer/commit/f8022b079e3a1c79f6b09810855d128ed93bf6be))

* refactor(Proof): abstract proof handler to centralize proof logic ([`4866a3b`](https://github.com/blockchain-certificates/cert-issuer/commit/4866a3b0a0d0b769078354f555d50cc33a3baa0a))

* refactor(Schema): properly instantiate class ([`58bf57e`](https://github.com/blockchain-certificates/cert-issuer/commit/58bf57e6657d188c9bd75e5f311a8e0a8d61bb3e))

* refactor(Schema): use latest cert-schema API ([`bcb534f`](https://github.com/blockchain-certificates/cert-issuer/commit/bcb534f1c9e47f5eaeef18cd9dde7f6cb647383b))

### Test

* test(Metadata): test issuance check ([`7444fac`](https://github.com/blockchain-certificates/cert-issuer/commit/7444fac3ce187c4340ce726d2970c954619ea763))

* test(Metadata): add tests for displayOrder and schema absence check ([`6601a04`](https://github.com/blockchain-certificates/cert-issuer/commit/6601a04105a2ef9f2fc957228167c40dd2b12a43))

* test(RFC3339): add more test cases ([`cd80945`](https://github.com/blockchain-certificates/cert-issuer/commit/cd80945bc0f6bad9a9c458edfa06773016d8cf66))

### Unknown

* Merge pull request #238 from blockchain-certificates/feat/validate_metadata

Feat/validate metadata ([`76c99cb`](https://github.com/blockchain-certificates/cert-issuer/commit/76c99cbaa32f06bbec347b6646d605d0f0aac510))

* Merge pull request #232 from blockchain-certificates/poc/proof-chain

Feat: proofChain with chainedProof2021 ([`b268ac4`](https://github.com/blockchain-certificates/cert-issuer/commit/b268ac4b1d54826e7301385120f6a5f1a2634c0c))

* Merge pull request #234 from koshilife/master

Correct the dead link of Merkle Proof Signature Suite 2019 ([`555cd46`](https://github.com/blockchain-certificates/cert-issuer/commit/555cd46b407a272842d08a1a28d5896f01cd1815))

* Correct the dead link of Merkle Proof Signature Suite 2019 ([`60e6c61`](https://github.com/blockchain-certificates/cert-issuer/commit/60e6c6177558029da61a44af31c4336c3fced085))

* Merge pull request #233 from shoito/patch-1

Correct link to DIF universal resolver ([`37f1ac0`](https://github.com/blockchain-certificates/cert-issuer/commit/37f1ac0a94c713ae514dbcf4ee0490e2915b6ab4))

* Correct link to DIF universal resolver ([`959e01c`](https://github.com/blockchain-certificates/cert-issuer/commit/959e01cb8b91a9c0e3162be39e52b56addb385fe))

* Style(CertificateHandler): remove trailing log instructions ([`9ec2260`](https://github.com/blockchain-certificates/cert-issuer/commit/9ec2260563eb6c4138b427423e6d83cfd3cb5910))

* poc(ChainedProof): sign with chainedProof ([`1d2e678`](https://github.com/blockchain-certificates/cert-issuer/commit/1d2e678c9bb63f4a327609fe6376096e5590d153))

* Merge pull request #230 from blockchain-certificates/feat/consume-cert-schema

Feat/consume cert schema ([`b9409a2`](https://github.com/blockchain-certificates/cert-issuer/commit/b9409a2f776664c77a1d9a160d8a7c6e45fb8dda))

* Merge pull request #228 from KhoiUna/readme-fix

fix readme ([`c62268d`](https://github.com/blockchain-certificates/cert-issuer/commit/c62268d749926347e632d290639d5ae695a34167))

* fix readme ([`50aca02`](https://github.com/blockchain-certificates/cert-issuer/commit/50aca028e836c8cee05185ff1dd9bc90798f4465))

* fix readme ([`c5f85ed`](https://github.com/blockchain-certificates/cert-issuer/commit/c5f85ed4a33d6198c71df5c5b4302eb8caad7b03))

* fix readme ([`c3f3bde`](https://github.com/blockchain-certificates/cert-issuer/commit/c3f3bdef3c471a79001d2d1b3141d11b533e55ee))

* fix readme ([`5058990`](https://github.com/blockchain-certificates/cert-issuer/commit/5058990ff01a5c56db683c19644a33006207fe79))

* Merge pull request #226 from KhoiUna/readme-fix

fix README.md: add more detailed instructions ([`33b1394`](https://github.com/blockchain-certificates/cert-issuer/commit/33b13943a6d79353bdc8e3ce0db2330ba174ae92))

* fix readme ([`5afa8e7`](https://github.com/blockchain-certificates/cert-issuer/commit/5afa8e75a1cf617b0a091019bebef540725486fc))

* fix readme ([`b4d0b30`](https://github.com/blockchain-certificates/cert-issuer/commit/b4d0b30fa7321a68d416721d1e19579dbf4d2b53))

* fix readme: bitcoin-cli -generate ([`aada0db`](https://github.com/blockchain-certificates/cert-issuer/commit/aada0db4a19ed4d106b20c34f9c445229790657a))

* fix README.md: add more detailed instructions ([`9b64dd9`](https://github.com/blockchain-certificates/cert-issuer/commit/9b64dd9a997f1739a53bbad3b5b03d15c420ea88))

* fix README.md: add more detailed instructions ([`d83a87d`](https://github.com/blockchain-certificates/cert-issuer/commit/d83a87d6ebf5b7f170749e171a3152de0617828c))

* Merge pull request #225 from KhoiUna/readme-fix

fix readme ([`50bde2a`](https://github.com/blockchain-certificates/cert-issuer/commit/50bde2ae4ba72a0e8d47260638ea635103a8374e))

* fix readme ([`8156b37`](https://github.com/blockchain-certificates/cert-issuer/commit/8156b37d6df398a1a946f59f3e957e899923565f))

* Merge pull request #224 from blockchain-certificates/fix/context-check

fix(Context): limit valid context addresses according to cert-schema preloading ([`a51608a`](https://github.com/blockchain-certificates/cert-issuer/commit/a51608a98033be4fca88df6d3708c98baba2907c))

* Merge pull request #222 from antonellopasella-kedos/patch-1

Move to a more updated image for bitcoind ([`cf8b581`](https://github.com/blockchain-certificates/cert-issuer/commit/cf8b581f7d9fd12c452733b41f12c188f3ba5e66))

* move to a more updated image for bitcoind

this will also support more architectures (like Apple M1 ones) ([`8013e87`](https://github.com/blockchain-certificates/cert-issuer/commit/8013e87039355a196bade71fa2b3690568be0d5c))

* Merge pull request #220 from blockchain-certificates/fix/v3-schema

fix(v3): ensure display is properly hashed ([`e1ea2c6`](https://github.com/blockchain-certificates/cert-issuer/commit/e1ea2c60e5af12884283bdc99160a5795c3783c8))

* Merge pull request #219 from blockchain-certificates/docs/examples

docs(v3): update examples ([`ad37a88`](https://github.com/blockchain-certificates/cert-issuer/commit/ad37a88441c23e327e5ba76c3a5cda60b0b2084c))

* Merge pull request #218 from blockchain-certificates/feat/check-context-order

feat(V3): provide check to make sure blockcerts context is last ([`d267c76`](https://github.com/blockchain-certificates/cert-issuer/commit/d267c7642e9f8ddda7d6d0af9c0439918a2ac4f0))

* Merge pull request #214 from blockchain-certificates/v3

V3 ([`eeb2c1d`](https://github.com/blockchain-certificates/cert-issuer/commit/eeb2c1d7c6b90eb9f09763ee84479b2fe447c0cc))

* Merge branch &#39;v3&#39; of https://github.com/blockchain-certificates/cert-issuer into v3 ([`d888f7d`](https://github.com/blockchain-certificates/cert-issuer/commit/d888f7d5cfc9062ab44ef1e126d6424270069f50))

* Merge branch &#39;master&#39; into v3 ([`db7d026`](https://github.com/blockchain-certificates/cert-issuer/commit/db7d026261f5bb3c8bdcae90bc25122f6148756d))

* Merge pull request #213 from blockchain-certificates/feat/v3-jf-updates

prevent captcha request when calling Etherscan ropsten API ([`99d244d`](https://github.com/blockchain-certificates/cert-issuer/commit/99d244d8fd2afc9f2fc6d2feea10b79d8427ffac))

* Merge branch &#39;v3&#39; of https://github.com/blockchain-certificates/cert-issuer into v3 ([`926c7d1`](https://github.com/blockchain-certificates/cert-issuer/commit/926c7d1b8bfa562ced6cc10fbf03175430ebbba4))

* Merge pull request #212 from Kedos-srl/fix_ropsten_url_changed

Ropsten API URL changed and the normal requests are blocked with a 40… ([`43191df`](https://github.com/blockchain-certificates/cert-issuer/commit/43191df9d8a37e92dbb35af40aec069cdca53475))

* Revving version. ([`510ee37`](https://github.com/blockchain-certificates/cert-issuer/commit/510ee370101a3887d7b7699bd6a62aa05f869948))

* Ropsten API URL changed and the normal requests are blocked with a 403 if the User Agent is python-requests. ([`5a4b7da`](https://github.com/blockchain-certificates/cert-issuer/commit/5a4b7da571f3d70a901a686bc6fb7bd81543fc3f))

* Merge pull request #208 from blockchain-certificates/fu_bad_dependencies

Fixed bad dependencies in the Dockerfile ([`6b4879a`](https://github.com/blockchain-certificates/cert-issuer/commit/6b4879a8076f468517ab02a58c61041c21df667f))

* #207 - Dealt with some dependency issues that prevented the Docker container from building. ([`73f25fa`](https://github.com/blockchain-certificates/cert-issuer/commit/73f25fa98c26e13351216f1d59cb8a677924b3bf))

* Updated some dependencies.  Let&#39;s hope it works. ([`e733298`](https://github.com/blockchain-certificates/cert-issuer/commit/e7332984b292a40c1b6b9704ddc55c49267be80f))

* #136 - Commented out MyEtherWallet bindings for now. ([`b7d2520`](https://github.com/blockchain-certificates/cert-issuer/commit/b7d252068e565d1323b283cb9d03a202b3b6e64d))

* Merge pull request #202 from blockchain-certificates/docs/sample-issuer

docs(Issuer): add fixed github URLs ([`a7fb942`](https://github.com/blockchain-certificates/cert-issuer/commit/a7fb9421780237cf9becbdafc81b61657ec07142))

* Merge pull request #201 from blockchain-certificates/docs/sample-issuer

docs(Issuer): add sample issuer details ([`eb3f6a2`](https://github.com/blockchain-certificates/cert-issuer/commit/eb3f6a2513af18e07cbe001b696dae627839895c))

* Merge pull request #196 from danishfastian/master

Certissuer fix related to BlockCypher configuration ([`c3c7233`](https://github.com/blockchain-certificates/cert-issuer/commit/c3c723346465d2fb396375217db6cf861808555e))
