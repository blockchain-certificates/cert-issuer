import os
from distutils.core import Command

from pip.req import parse_requirements
from setuptools import find_packages
from setuptools import setup

from cert_issuer import __version__

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

install_reqs = parse_requirements('bitcoin_requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]


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
            install_reqs = parse_requirements('ethereum_requirements.txt', session=False)
            eth_reqs = [str(ir.req) for ir in install_reqs]
            reqs.append(eth_reqs)


setup(
    cmdclass={
        'blockchain': InstallCommand
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
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'cert-issuer = cert_issuer.__main__:cert_issuer_main',
        ]
    },
    packages=find_packages()
)
