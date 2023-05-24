cp node_modules/vc-test-suite/implementations/index.html ./vc-compliance-report.html
git status
git add ./vc-compliance-report.html
git commit -m "chore(Compliance): update compliance report"
git push origin $TRAVIS_BRANCH
