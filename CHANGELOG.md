# CHANGELOG


## v3.8.0 (2024-11-07)

### Chores

* chore(CI): change twine upload prompt place to access env var ([`48059c5`](https://github.com/blockchain-certificates/cert-issuer/commit/48059c52d62f0723f5a6e3872c87275f5e505b15))

### Features

* feat(CredentialSubject): handle multiple credential subjects ([`3434701`](https://github.com/blockchain-certificates/cert-issuer/commit/34347012d137f96f8d7d179d7d8f0c798f39cfd9))

* feat(Schemas): bump schema version ([`f9d79db`](https://github.com/blockchain-certificates/cert-issuer/commit/f9d79db825a1dcd49487e98e9790f984801984e3))

* feat(VCv2): bump cert-schema ([`f32d889`](https://github.com/blockchain-certificates/cert-issuer/commit/f32d889793c7c308abacb41ef5d3ef69c72d49f4))

### Testing

* test(CredentialSubject): add null test ([`cd605bd`](https://github.com/blockchain-certificates/cert-issuer/commit/cd605bd126233c5f12c274c9737c28efcd2b0663))

### Unknown

* Merge pull request #304 from blockchain-certificates/feat/vc-v2-name-description

Support credential subject as array ([`deafa4a`](https://github.com/blockchain-certificates/cert-issuer/commit/deafa4a3169501695b2c3d09667a845c14ad4787))

* Merge pull request #303 from blockchain-certificates/chore/fix-semantic-release

chore(CI): change twine upload prompt place to access env var ([`023d197`](https://github.com/blockchain-certificates/cert-issuer/commit/023d1971dd4459994b1fcd9299529b5e26b2d2a2))

* Merge pull request #302 from blockchain-certificates/fix/proof-and-date-validity

chore(Release): manual release 3.7.0 ([`a9039e4`](https://github.com/blockchain-certificates/cert-issuer/commit/a9039e464139a5642e4d963beac65253f0cbd8b3))


## v3.7.0 (2024-10-16)

### Bug Fixes

* fix(Datetime): follow datetime spec from VC v2 ([`c94e909`](https://github.com/blockchain-certificates/cert-issuer/commit/c94e909e5570a883c210e20f8a87728e3d401f57))

* fix(Eth): update variable name from web3 ([`de2f5f0`](https://github.com/blockchain-certificates/cert-issuer/commit/de2f5f0e5d9646e531164a8b65aad2cb2dde42d6))

* fix(Issue#286): add missing argument for CertificateV3Handler constructor ([`99db9d4`](https://github.com/blockchain-certificates/cert-issuer/commit/99db9d4541e80918a72e97e5a907f8bd44914370))

### Chores

* chore(Release): manual release 3.7.0 ([`f617cdc`](https://github.com/blockchain-certificates/cert-issuer/commit/f617cdc2b366be1e1f96d0bc383f27dca4cc2cc5))

* chore(CI): disable password and use TWINE_NON_INTERACTIVE in travis env ([`b750e9d`](https://github.com/blockchain-certificates/cert-issuer/commit/b750e9d27b7f5c6faf0e7b12a2ee17d5a7b70028))

* chore(CI): re-enable password param in TWINE to avoid manual prompt in Travis ([`a4f8663`](https://github.com/blockchain-certificates/cert-issuer/commit/a4f8663d2b4967b1febe182a24933ce90fcba3e7))

* chore(CI): enable twine upload. maybe? ([`d328593`](https://github.com/blockchain-certificates/cert-issuer/commit/d32859379fe2e4471dc8c2c37080ddc809c3ba39))

* chore(CI): debug twine upload ([`b663361`](https://github.com/blockchain-certificates/cert-issuer/commit/b663361966411fd24cc2c0d5dcc702b11b9a41fb))

* chore(CI): debug twine upload ([`e436941`](https://github.com/blockchain-certificates/cert-issuer/commit/e436941ea5494811d4a429ed669da0cd79dcd718))

* chore(CI): debug twine upload error ([`1d435fe`](https://github.com/blockchain-certificates/cert-issuer/commit/1d435fecac8c5e4d52680eb20b07bcb55c4187e0))

* chore(CI): attempt fixing semantic release publish ([`a226f10`](https://github.com/blockchain-certificates/cert-issuer/commit/a226f10ca5d24d27ba298b118796c6e241f7ab51))

* chore(CI): disable keyring

as per https://twine.readthedocs.io/en/latest/index.html#disabling-keyring ([`3830290`](https://github.com/blockchain-certificates/cert-issuer/commit/38302902f481a212cfac5d8353738d222b5645f3))

* chore(vc-test-suite): do not test in chained proof mode ([`aff09fa`](https://github.com/blockchain-certificates/cert-issuer/commit/aff09faf993693f437f51932c7c8f8d214ef4463))

* chore(vc-test-suite): download vc example context and allow usage by jsonld document loader ([`1f4e75d`](https://github.com/blockchain-certificates/cert-issuer/commit/1f4e75d415327457a560749bbde34603d5789e35))

* chore(vc-test-suite): bump dep ([`5f43887`](https://github.com/blockchain-certificates/cert-issuer/commit/5f43887981d452dc11bf10cea5ab6040fcd36565))

* chore(vc-test-suite): declare work dir in test conf.ini ([`a60ea4d`](https://github.com/blockchain-certificates/cert-issuer/commit/a60ea4de7924b1ed58fdfe418700a5f795effb6f))

* chore(vc-test-suite): update dep ([`c08ca62`](https://github.com/blockchain-certificates/cert-issuer/commit/c08ca62b00e66f01788da06168c00c5a1b512ea5))

* chore(vc-test-suite): update dep ([`73441dc`](https://github.com/blockchain-certificates/cert-issuer/commit/73441dc3a91c67c3839dc22ace5f05eaa78d3f88))

* chore(vc-test-suite): update dep ([`03e37e9`](https://github.com/blockchain-certificates/cert-issuer/commit/03e37e9d58cbd9d71237700773f4510f86b766fa))

* chore(vc-test-suite): update dep ([`6d5c365`](https://github.com/blockchain-certificates/cert-issuer/commit/6d5c3653d5bb11533455d765cf01aca08d23a0f4))

* chore(Compliance): update compliance status ([`6a64c16`](https://github.com/blockchain-certificates/cert-issuer/commit/6a64c169b346b59adb8ac44e75cfb50bef7a2438))

* chore(Compliance): update compliance status ([`db3cf57`](https://github.com/blockchain-certificates/cert-issuer/commit/db3cf57424d9ac7654da2d2e8b5047a6d1194043))

* chore(Compliance): update compliance status ([`2834ae3`](https://github.com/blockchain-certificates/cert-issuer/commit/2834ae3579fd5df482229e20648387f72321f81a))

* chore(SemanticRelease): abstract to own bash script ([`24b1521`](https://github.com/blockchain-certificates/cert-issuer/commit/24b152125e29be050e6b938ffa78593536271c62))

### Features

* feat: removed code reps ([`b16a97f`](https://github.com/blockchain-certificates/cert-issuer/commit/b16a97ffefa0d409c6ca49865fd199d94c8488cc))

* feat: gas_price method moved to the right class ([`c9d5ee6`](https://github.com/blockchain-certificates/cert-issuer/commit/c9d5ee677fb1ec2e6f4701271c49a98a8e511c47))

* feat: fetching gas price from etherscan based on a config ([`f9562b3`](https://github.com/blockchain-certificates/cert-issuer/commit/f9562b3313586fcc0207110d5c8e83c66c2b2367))

* feat: supporting ethereum chain using the existing issue API ([`0f676d6`](https://github.com/blockchain-certificates/cert-issuer/commit/0f676d69ddeb84b20ad77cf0597390e48d40ec08))

* feat: support for issuing credentials into the eth chains via API ([`1763f04`](https://github.com/blockchain-certificates/cert-issuer/commit/1763f0479bc26fb45318a7efeb036604c733e718))

### Testing

* test(issuer): ensure issuer cannot be an array ([`000ef0e`](https://github.com/blockchain-certificates/cert-issuer/commit/000ef0e4579596c9233fa78249dab1881870e0fd))

### Unknown

* Merge pull request #301 from blockchain-certificates/fix/proof-and-date-validity

chore(CI): disable password and use TWINE_NON_INTERACTIVE in travis env ([`2b75eb8`](https://github.com/blockchain-certificates/cert-issuer/commit/2b75eb8c6eafd13d8ae590f979e39d394e619e3a))

* Merge pull request #300 from blockchain-certificates/fix/proof-and-date-validity

chore(CI): re-enable password param in TWINE to avoid manual prompt i… ([`c26fae7`](https://github.com/blockchain-certificates/cert-issuer/commit/c26fae7cebbae674278669a0312284187b8bee44))

* Merge pull request #299 from blockchain-certificates/fix/proof-and-date-validity

chore(CI): enable twine upload. maybe? ([`446f05b`](https://github.com/blockchain-certificates/cert-issuer/commit/446f05b2e03e5949b31af9c413ecb68123926d3b))

* Merge pull request #298 from blockchain-certificates/fix/proof-and-date-validity

chore(CI): debug twine upload ([`a2d5eab`](https://github.com/blockchain-certificates/cert-issuer/commit/a2d5eab019996e2469a40bf606dbd4ea48b2b58b))

* Merge pull request #297 from blockchain-certificates/fix/proof-and-date-validity

chore(CI): debug twine upload ([`c5c70e1`](https://github.com/blockchain-certificates/cert-issuer/commit/c5c70e15d959672daf4cc09adbb61b4edd272884))

* Merge pull request #296 from blockchain-certificates/fix/proof-and-date-validity

chore(CI): debug twine upload error ([`dc6e51d`](https://github.com/blockchain-certificates/cert-issuer/commit/dc6e51dadee5aafbf60ca6cbd83168454afe6da3))

* Merge pull request #295 from blockchain-certificates/fix/proof-and-date-validity

chore(CI): attempt fixing semantic release publish ([`5658d49`](https://github.com/blockchain-certificates/cert-issuer/commit/5658d49270d2f2edd4bca2912185bd8f9c42290e))

* Merge pull request #294 from blockchain-certificates/fix/proof-and-date-validity

fix(Datetime): follow datetime spec from VC v2 ([`471ca3c`](https://github.com/blockchain-certificates/cert-issuer/commit/471ca3ccfff3d6091001b0acc48e5446f3cb8c96))

* Merge pull request #292 from blockchain-certificates/fix/eth-issuance

fix(Eth): update variable name from web3 ([`f1b92cf`](https://github.com/blockchain-certificates/cert-issuer/commit/f1b92cf9d7053b7467d00b62a938933d143d854d))

* Merge pull request #291 from blockchain-certificates/chore/ci-twine-keyring

Chore/ci twine keyring ([`d6ce0b7`](https://github.com/blockchain-certificates/cert-issuer/commit/d6ce0b78a4bd8d62b3706db39a4b8c5473d65469))

* Merge branch 'master' of https://github.com/blockchain-certificates/cert-issuer into chore/ci-twine-keyring ([`0b37e3c`](https://github.com/blockchain-certificates/cert-issuer/commit/0b37e3cf695a1e2d50bb4c6c019659c093c6500b))

* Merge pull request #289 from abhisheksarka/feature/issue_certs_on_ethereum_chain_via_api

Support for issuing Credentials to the Ethereum Blockchain via API ([`863e5ed`](https://github.com/blockchain-certificates/cert-issuer/commit/863e5ed29e02b4d1d18aca4d3912911b3e410fce))

* Merge branch 'master' into feature/issue_certs_on_ethereum_chain_via_api ([`0b4492a`](https://github.com/blockchain-certificates/cert-issuer/commit/0b4492a0554aa18291bf68e4e0bc394ce59496b2))

* Merge pull request #288 from san-esc/master

Fix missing argument for CertificateV3Handler constructor ([`1e59dbc`](https://github.com/blockchain-certificates/cert-issuer/commit/1e59dbc1846e9368688b3388ee1932fa7df000ca))

* Merge pull request #287 from abhisheksarka/feature/dynamic_gas_price

Fetching current gas price from Etherscan ([`ce8947e`](https://github.com/blockchain-certificates/cert-issuer/commit/ce8947ebd4ce88f4c690e196681e0866f69a4cf0))

* Merge pull request #280 from blockchain-certificates/chore/fix-vc-test-suite-report

Chore/fix vc test suite report ([`6f5a042`](https://github.com/blockchain-certificates/cert-issuer/commit/6f5a0427cb6e270aa735232002112ddaeb589f77))

* Merge pull request #279 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): abstract to own bash script ([`6932041`](https://github.com/blockchain-certificates/cert-issuer/commit/693204136e611dace9a6184dc6d9e55ac1dfa8b3))


## v3.6.0 (2024-03-07)

### Bug Fixes

* fix(Deps): remove unused dependency ([`94d3f83`](https://github.com/blockchain-certificates/cert-issuer/commit/94d3f839f6ee2581f95aaded7bd47e7c838209df))

### Chores

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

Signed-off-by: dependabot[bot] <support@github.com> ([`0383454`](https://github.com/blockchain-certificates/cert-issuer/commit/0383454152de92ad8a5db4d30c967dc6c5a4b032))

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

Signed-off-by: dependabot[bot] <support@github.com> ([`18f78a6`](https://github.com/blockchain-certificates/cert-issuer/commit/18f78a6ed19dbf56343264b0fae12076f2ee679f))

### Features

* feat(CredentialSubject): compare credential subject against credential schema before issuance ([`2618b20`](https://github.com/blockchain-certificates/cert-issuer/commit/2618b20752d2a1da8c40f0e8fe8488083223fc12))

* feat(CredentialSchema): verify credentialSchema property validity ([`77d219b`](https://github.com/blockchain-certificates/cert-issuer/commit/77d219b5437a20ade67ea4343931fa39420f6738))

* feat(DataIntegrityProof): handle contexts for data integrity proof ([`b13182b`](https://github.com/blockchain-certificates/cert-issuer/commit/b13182b6b6b8a07b529f986a2caa11ed177a93ef))

* feat(Vc-V2): bump deeps ([`0c83ef1`](https://github.com/blockchain-certificates/cert-issuer/commit/0c83ef1d74b1df660c24e4a6817cbeeec6ff7081))

* feat(Vc-V2): verify expirationDate/validUntil is set after issuanceDate/validFrom ([`eaf47c8`](https://github.com/blockchain-certificates/cert-issuer/commit/eaf47c8a4f5f320516f329964f2b23716bb4348f))

* feat(Vc-V2): add validFrom/validUntil verification ([`cb41e73`](https://github.com/blockchain-certificates/cert-issuer/commit/cb41e73831e36f1edfe8da91932571072bac4914))

* feat(Vc-V2): prevent having both v1 and v2 vc context defined ([`f46dffa`](https://github.com/blockchain-certificates/cert-issuer/commit/f46dffac072c20d5a925aec2ce56210eb63429ca))

* feat(Vc-V2): allow VC v2 context in cert ([`d942606`](https://github.com/blockchain-certificates/cert-issuer/commit/d9426063d7c5781ec14f6926023838ae04f1dd49))

* feat(Vc-V2): bump cert-schema ([`c70f0b5`](https://github.com/blockchain-certificates/cert-issuer/commit/c70f0b553f8d2c825b7852c1a52135d61d5a8002))

* feat(DataIntegrityProof): handle chained proofs according to DataIntegrityProof spec ([`601a216`](https://github.com/blockchain-certificates/cert-issuer/commit/601a2168ab6b3bc00f73fb58266748d5940c43a6))

* feat(DataIntegrityProof): add id to proof ([`814cede`](https://github.com/blockchain-certificates/cert-issuer/commit/814cede6ef80d6c4e9be417eb2e879431ef92353))

* feat(DataIntegrityProof): convert proof format to data integrity proof ([`5f9215e`](https://github.com/blockchain-certificates/cert-issuer/commit/5f9215ea769f9f54541089286dc67f7bd330679d))

### Refactoring

* refactor(DataIntegrityProof): remove chainedProof2021 class ([`96c6abe`](https://github.com/blockchain-certificates/cert-issuer/commit/96c6abe1a4dbb8e4471598057a0403e70f0df664))

* refactor(DataIntegrityProof): move responsibility of creating proof object to proof handler ([`4b20423`](https://github.com/blockchain-certificates/cert-issuer/commit/4b20423afc257881c4e1ca84a8e1b87d61820dba))

* refactor(DataIntegrityProof): extract merkle proof 2019 to its own constructor ([`889440b`](https://github.com/blockchain-certificates/cert-issuer/commit/889440b7c2fc605861d46325da14401682db901b))

### Unknown

* Merge pull request #278 from blockchain-certificates/chore/fix-semantic-release

chore(SemanticRelease): install twine ([`03f398d`](https://github.com/blockchain-certificates/cert-issuer/commit/03f398d265d3d6cc433a3212cee03c8d865d34c1))

* Merge pull request #277 from blockchain-certificates/chore/fix-semantic-release

Chore/fix semantic release ([`3ce03fd`](https://github.com/blockchain-certificates/cert-issuer/commit/3ce03fd7cc06609d494193bf3923ba2d44e788eb))

* Revert "chore(SemanticRelease): revert to v7 with support for pypi uplaod"

This reverts commit 0f2fc9a34513940ed8ed788e4a27a3ed5fb68c37. ([`c701a12`](https://github.com/blockchain-certificates/cert-issuer/commit/c701a12de13c7aaad0124bb80c2b9e4edeb975bc))

* Revert "chore(SemanticRelease): run only on merge build"

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

* Merge branch 'master' of https://github.com/blockchain-certificates/cert-issuer into feat/follow-data-integrity-proof ([`3dc65ff`](https://github.com/blockchain-certificates/cert-issuer/commit/3dc65ffc4258e57323fbe191c761f4e1dc4db9e0))

* Merge pull request #265 from blockchain-certificates/feat/vc-v2-validFrom-validUntil

Feat/vc v2 valid from valid until ([`19a2fc3`](https://github.com/blockchain-certificates/cert-issuer/commit/19a2fc3e43dd1d7a8fa41ff00e37ee7bc98dcd0c))

* Merge pull request #263 from blockchain-certificates/dependabot/npm_and_yarn/get-func-name-2.0.2

chore(deps): bump get-func-name from 2.0.0 to 2.0.2 ([`41c4550`](https://github.com/blockchain-certificates/cert-issuer/commit/41c45500587dbdbc32c590552fe1af23082bd582))

* Merge pull request #264 from blockchain-certificates/fix/update-deps

fix(Deps): remove unused dependency ([`6df70eb`](https://github.com/blockchain-certificates/cert-issuer/commit/6df70eb2fb3b971f1618911a72e7044e115c9757))

* Merge pull request #258 from blockchain-certificates/dependabot/npm_and_yarn/semver-5.7.2

chore(deps): bump semver from 5.7.1 to 5.7.2 ([`d8d36f5`](https://github.com/blockchain-certificates/cert-issuer/commit/d8d36f5e207dee130ed2e08858b2f80ab919d992))


## v3.5.0 (2023-06-07)

### Chores

* chore(Compliance): update compliance status ([`acfd4b7`](https://github.com/blockchain-certificates/cert-issuer/commit/acfd4b73cda3d766daf2087bc91aef65a310d7d2))

* chore(CI): revert run on PR branch ([`65f4150`](https://github.com/blockchain-certificates/cert-issuer/commit/65f4150ee5b3bbb2001e426fb290ce542d4b6503))

* chore(Compliance): publish compliance report on blockcerts.org ([`4506058`](https://github.com/blockchain-certificates/cert-issuer/commit/450605860f7d7fdad5faa91399a6b247c94cc81c))

* chore(Compliance): run publish report only on PR ([`5d83c48`](https://github.com/blockchain-certificates/cert-issuer/commit/5d83c48675dfbf7e34c8fc5e160af5610bc61221))

### Unknown

* Merge pull request #256 from blockchain-certificates/feat/multiple-signatures-non-chained

Support non chained signatures ([`b4d939e`](https://github.com/blockchain-certificates/cert-issuer/commit/b4d939e9a3546bd1e762be17b7a71831aaeb77ad))

* Revert "feat(ConcurrentProofs): chain sign concurrent proofs with merkle root of previous proofs"

This reverts commit 8449a9bc8798ce29759e5c1ba95d1919b0ae9a64. ([`1ecd92f`](https://github.com/blockchain-certificates/cert-issuer/commit/1ecd92f5b895ba2f4f6ad9570ae85b41b46d40b7))

* Merge branch 'master' of https://github.com/blockchain-certificates/cert-issuer into feat/concurrent-signatures ([`3461408`](https://github.com/blockchain-certificates/cert-issuer/commit/3461408df9556405683c0d3fc4674a871c61e095))

* Merge pull request #255 from blockchain-certificates/test/vc-compliance

chore(Compliance): publish compliance report on blockcerts.org ([`45dd96c`](https://github.com/blockchain-certificates/cert-issuer/commit/45dd96c7e6e86070257a41b4b7231eed4860f2b1))

* Merge pull request #254 from blockchain-certificates/test/vc-compliance

chore(Compliance): run publish report only on PR ([`9fde14f`](https://github.com/blockchain-certificates/cert-issuer/commit/9fde14fe9e85b1d74f3105444617b8571e351166))


## v3.4.0 (2023-05-26)

### Chores

* chore(Compliance): run publish only on PR ([`1413e52`](https://github.com/blockchain-certificates/cert-issuer/commit/1413e52e5cdbf8992e3c7df8ff1163861ac40e07))

* chore(CI): only build master ([`8941ab6`](https://github.com/blockchain-certificates/cert-issuer/commit/8941ab6f7bd5cb019a77a9e4fec71515010365d9))

* chore(Compliance): update compliance report ([`3b3eeee`](https://github.com/blockchain-certificates/cert-issuer/commit/3b3eeee67ade61ac2c96ab735653eda4a3cfefdc))

* chore(CI): only run on master branch ([`65d50b3`](https://github.com/blockchain-certificates/cert-issuer/commit/65d50b3949189faf84624c552d4ad49578ceb996))

* chore(CI): fix typo ([`102bad4`](https://github.com/blockchain-certificates/cert-issuer/commit/102bad40e0ad8cbee9f5a3854d15ac5253380aa8))

* chore(version): bump version and update dependencies ([`a643fff`](https://github.com/blockchain-certificates/cert-issuer/commit/a643fff114acbb29f2575710a5277e1925cc8a15))

### Unknown

* Merge pull request #251 from blockchain-certificates/test/vc-compliance

Test/vc compliance ([`9133b17`](https://github.com/blockchain-certificates/cert-issuer/commit/9133b17b42053efd91b768547caa9fed22f70ad2))

* Merge branch 'test/vc-compliance' of https://github.com/blockchain-certificates/cert-issuer into test/vc-compliance ([`368f1b0`](https://github.com/blockchain-certificates/cert-issuer/commit/368f1b0ae17045fc99c2270d4080d3af178c624a))

* Merge pull request #239 from digit-ink/master

Enable EIP-1559 ETH txs and update deprecated web3 methods/packages ([`48420fa`](https://github.com/blockchain-certificates/cert-issuer/commit/48420face863658f9412472ce2ce8e823b345581))

* update UnableToSignTxError() and delete redundant variable ([`107cd83`](https://github.com/blockchain-certificates/cert-issuer/commit/107cd83e9f7e55333673b1cadcee66771f1b0669))

* Enable EIP-1559-compliant ETH transactions and update deprecated web3 methods/packages ([`4f293b3`](https://github.com/blockchain-certificates/cert-issuer/commit/4f293b351127e1e0d791a1d7a44f1a582a90feaa))

* Merge pull request #237 from koshilife/support-goerli-and-sepolia

Support Ethereum testnets, the Goerli and the Sepolia ([`323601a`](https://github.com/blockchain-certificates/cert-issuer/commit/323601a50e5fe111ea03054eef60bebc651a86ec))


## v3.2.0 (2022-07-12)

### Features

* feat(StatusList): support issuance of array credentialStatus property value ([`71cabce`](https://github.com/blockchain-certificates/cert-issuer/commit/71cabce20191dc5b56279c00adcc7831fd89ca1f))

* feat(ConcurrentProofs): chain sign concurrent proofs with merkle root of previous proofs ([`8449a9b`](https://github.com/blockchain-certificates/cert-issuer/commit/8449a9bc8798ce29759e5c1ba95d1919b0ae9a64))

* feat(ConcurrentProofs): allow setting nature of multiple proofs by config/CLI ([`6ebf7f1`](https://github.com/blockchain-certificates/cert-issuer/commit/6ebf7f142105d5373d356cdce2d3be33310a2041))

* feat(ProofHandler): add concurrent proof ([`8670875`](https://github.com/blockchain-certificates/cert-issuer/commit/867087522e20774aa8f2301ec89808207a544c2b))

### Refactoring

* refactor(ProofHandler): add chained flag ([`29f91bb`](https://github.com/blockchain-certificates/cert-issuer/commit/29f91bb2a6cf3786c0e026f13c96b4a593fe9f15))

### Unknown

* Merge pull request #238 from blockchain-certificates/feat/validate_metadata

Feat/validate metadata ([`76c99cb`](https://github.com/blockchain-certificates/cert-issuer/commit/76c99cbaa32f06bbec347b6646d605d0f0aac510))

* Merge pull request #253 from blockchain-certificates/feat/status-list-2021

feat(StatusList): support issuance of array credentialStatus property… ([`a34a9ac`](https://github.com/blockchain-certificates/cert-issuer/commit/a34a9acefd24b38ddd324530e548a1ea47949f0c))

* Merge pull request #248 from dallarosa/dallarosa-fix-dockerfile-regtest

fix Dockerfile ([`2414aa2`](https://github.com/blockchain-certificates/cert-issuer/commit/2414aa2758148b32a4cedcee702d14c58b7bce14))

* fix Dockerfile

Added the header [regtest] to bitcoin.conf, fixing the error:
"Error: Config setting for -rpcport only applied on regtest network when in [regtest] section." ([`c528638`](https://github.com/blockchain-certificates/cert-issuer/commit/c5286388d9bc09ebec4e9119323f8dc0c55f00ce))


## v3.3.0 (2022-08-25)

### Chores

* chore(CI): enable semantic release for real ([`ed3d51b`](https://github.com/blockchain-certificates/cert-issuer/commit/ed3d51b72a0c361e739ddaee9c5c9c8fc41f2039))

### Unknown

* Merge pull request #245 from blockchain-certificates/chore/semantic-release

chore(CI): enable semantic release for real ([`3d07ec8`](https://github.com/blockchain-certificates/cert-issuer/commit/3d07ec8997aadc9639a02789d841e8d1250cac29))

* Merge pull request #244 from blockchain-certificates/chore/semantic-release

chore(CI): configure semantic release to pick up version from tag ([`3dd6aa8`](https://github.com/blockchain-certificates/cert-issuer/commit/3dd6aa8a3539b321f8863304308f27a75632b052))
