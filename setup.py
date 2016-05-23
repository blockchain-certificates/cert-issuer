import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

setup(
    name='certificate-issuer',
    version='0.0.1',
    url='https://github.com/ml-learning/digital-certificates-v2',
    license='MIT',
    author='MIT Media Labs certificates',
    author_email='coins@media.mit.edu',
    description='',
    packages=['certificate_issuer'],
    include_package_data=True,
    install_requires=[
        'pycoin==0.62',
        'requests==2.9.1',
        'glob2==0.4.1',
        'configargparse==0.10.0',
        'python-bitcoinlib==0.5.0',
        'mock==2.0.0',
        'tox==2.3.1'
    ], )
