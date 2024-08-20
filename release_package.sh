#!/usr/bin/env bash

rm -rf dist
python3 setup.py sdist bdist_wheel
keyring --disable
twine upload dist/*
