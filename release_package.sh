#!/usr/bin/env bash

rm -rf dist
python3 setup.py sdist bdist_wheel
keyring --disable
echo $TWINE_USERNAME
echo $TWINE_PASSWORD
twine upload dist/* -u%$TWINE_USERNAME% -p%$TWINE_PASSWORD% --verbose
