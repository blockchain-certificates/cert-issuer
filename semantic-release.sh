#!/usr/bin/env bash

pip install python-semantic-release twine
git config user.name botcerts
git config user.email botcerts@learningmachine.com
git checkout master
semantic-release version
source ./release_package.sh