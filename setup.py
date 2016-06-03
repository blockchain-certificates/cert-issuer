import os
from pip.req import parse_requirements
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

setup(
    name='cert-issuer',
    version='0.0.1',
    url='https://github.com/digital-certificates/cert-issuer',
    license='MIT',
    author='MIT Media Lab Digital Certificates',
    author_email='certs@media.mit.edu',
    description='Issues digital certificates using the Bitcoin blockchain',
    long_description=long_description,
    packages=['cert_issuer'],
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'cert-issuer = cert_issuer.__main__:main'
        ]
    }
)
