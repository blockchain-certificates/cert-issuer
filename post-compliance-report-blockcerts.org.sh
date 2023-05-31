#!/usr/bin/env bash

# automate PR process to Blockcerts.org: update vc compliance test suite result
GITHUB_COM=github.com
BLOCKCERTS_GITHUB_REPO=blockchain-certificates-web/blockchain-certificates-web.github.io
GIT_REPO=$GITHUB_COM/$BLOCKCERTS_GITHUB_REPO.git
WORK_BRANCH=feat/update-vc-compliance-report
GITHUB_USER=botcerts

# clone CTS repo
git clone https://$GIT_REPO
cd blockchain-certificates-web.github.io

# rename remote to add authentication
git remote rm origin
git remote add origin https://$GITHUB_USER:$BOTCERTS_PR_GITHUB_TOKEN@$GIT_REPO

# copy report
git checkout -b $WORK_BRANCH
cp ../node_modules/vc-test-suite/implementations/index.html ./vc-compliance-report.html
git add vc-compliance-report.html
git commit -m "docs(Compliance): update vc compliance report"
git push origin $WORK_BRANCH

# open PR
curl --data '{"head":"'${WORK_BRANCH}'", "base":"master", "title": "update VC compliance test suite result", "body": "Please review and merge @lemoustachiste @raiseandfall"}' -H "Authorization: token ${BOTCERTS_PR_GITHUB_TOKEN}" https://api.github.com/repos/$BLOCKCERTS_GITHUB_REPO/pulls -v

# clean after use
cd ..
echo 'Delete working directory'
rm -rf blockchain-certificates.github.io