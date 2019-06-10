import os
from distutils.core import Command

import subprocess
import sys
from setuptools import find_packages
from setuptools import setup

from cert_issuer import __version__

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

with open('requirements.txt') as f:
    install_reqs = f.readlines()
    reqs = [str(ir) for ir in install_reqs]


class InstallCommand(Command):
    description = "Installs Blockcerts cert-issuer with optional blockchain argument."
    user_options = [
        ('blockchain=', None, 'Specify the blockchain. Bitcoin (default) or ethereum.'),
    ]

    def initialize_options(self):
        self.blockchain = 'bitcoin'

    def finalize_options(self):
        assert self.blockchain in ('bitcoin', 'ethereum'), 'Invalid blockchain!'

    def run(self):
        if self.blockchain == 'ethereum':
            with open('ethereum_requirements.txt') as f:
                install_reqs = f.readlines()
                eth_reqs = [str(ir) for ir in install_reqs]
                reqs.extend(eth_reqs)
        else:
            with open('bitcoin_requirements.txt') as f:
                install_reqs = f.readlines()
                btc_reqs = [str(ir) for ir in install_reqs]
                reqs.extend(btc_reqs)
        install(reqs)

def install(packages):
    for package in packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


setup(
    cmdclass={
        'experimental': InstallCommand
    },
    install_requires=reqs,
    name='cert-issuer',
    version=__version__,
    url='https://github.com/blockchain-certificates/cert-issuer',
    license='MIT',
    author='Blockcerts',
    author_email='info@blockcerts.org',
    description='Issues blockchain certificates using the Bitcoin blockchain',
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cert-issuer = cert_issuer.__main__:cert_issuer_main',
        ]
    },
    packages=find_packages()
)
