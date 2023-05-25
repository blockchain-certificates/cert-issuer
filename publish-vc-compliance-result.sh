cp node_modules/vc-test-suite/implementations/index.html ./vc-compliance-report.html
git status
git add vc-compliance-report.html
git commit -m "chore(Compliance): update compliance report"
git config --list
echo "Pushing changes to $TRAVIS_BRANCH"
git config credential.helper "store --file=.git/credentials"
echo "https://${GH_TOKEN}:@github.com" > .git/credentials
git push origin $TRAVIS_BRANCH --verbose
