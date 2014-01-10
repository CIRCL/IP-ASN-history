#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

try:
       from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
       from distutils.command.build_py import build_py

setup(
    name='ipasn_web',
    version='1.0.2',
    description='Library to access the IP ASN History REST API.',
    url='https://github.com/CIRCL/IP-ASN-history',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    packages=['ipasn'],
    cmdclass = {'build_py': build_py},
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

    requires=['requests']

    )
