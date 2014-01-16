#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='ipasn-redis',
    version='1.0',
    description='API to access an IP-ASN-history instance via Redis.',
    url='https://github.com/CIRCL/IP-ASN-history',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    packages=['ipasn', 'ipasn.redis'],
    scripts = ['bin/ipasn_redis', 'bin/ipasn-fullhistory_redis'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Programming Language :: Python',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: System :: Networking',
        ],

    install_requires=['redis']

    )
