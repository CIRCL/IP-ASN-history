#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py


setup(
    name='ip_asn_history',
    version='1.0.3',
    description='API to access an IP-ASN-history instance.',
    url='https://github.com/CIRCL/IP-ASN-history',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    packages=['ip_asn_history'],
    cmdclass = {'build_py': build_py},
    scripts = ['ip2asn_asn', 'ip2asn_fullhistory'],
    long_description=open('../README.md').read(),
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

    requires=['redis']

    )
