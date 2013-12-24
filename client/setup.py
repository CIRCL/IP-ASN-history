#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='ip_asn_history',
    version='1.0.1',
    description='API to access an IP-ASN-history instance.',
    url='https://github.com/CIRCL/IP-ASN-history',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    maintainer_email='raphael.vinot@circl.lu',
    packages=['ip_asn_history'],
    scripts = ['ip2asn_asn', 'ip2asn_fullhistory'],
    license='GNU AGPLv3',
    long_description=open('../README.md').read(),
    )
