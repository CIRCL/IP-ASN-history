#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='ipasn-web',
    version='1.0',
    description='Library to access the IP ASN History REST API.',
    url='https://github.com/CIRCL/IP-ASN-history',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    packages=['ipasn', 'ipasn.web'],
    scripts = ['bin/ipasn_web', 'bin/ipasn-fullhistory_web'],
    long_description=open('README.md').read(),
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

    install_requires=['requests']

    )
