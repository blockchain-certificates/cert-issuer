import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

setup(
    name='issuer',
    version='0.0.1',
    url='https://github.com/digital-certificates/issuer',
    license='MIT',
    author='MIT Media Lab Digital Certificates',
    author_email='coins@media.mit.edu',
    description='',
    packages=['issuer'],
    include_package_data=True,
    install_requires=[
        'pycoin==0.62',
        'requests==2.9.1',
        'glob2==0.4.1',
        'configargparse==0.10.0',
        'python-bitcoinlib==0.5.0',
        'mock==2.0.0',
        'tox==2.3.1',
        'recommonmark==0.4.0',
        'Sphinx>=1.4.1',
        'sphinx-rtd-theme>=0.1.9'
    ], )
