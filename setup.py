import os
from pip.req import parse_requirements
from setuptools import setup, find_packages
from cert_issuer import __version__

here = os.path.abspath(os.path.dirname(__file__))

install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

setup(
    name='cert-issuer',
    version=__version__,
    url='https://github.com/blockchain-certificates/cert-issuer',
    license='MIT',
    author='Blockcerts',
    author_email='info@blockcerts.org',
    description='Issues blockchain certificates using the Bitcoin blockchain',
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'cert-issuer = cert_issuer.__main__:cert_issuer_main',
        ]
    }
)

