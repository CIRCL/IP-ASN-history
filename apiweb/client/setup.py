#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

try:
       from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
       from distutils.command.build_py import build_py

setup(
    name='ipasn_web',
    version='1.0',
    description='Library to access the IP ASN History REST API.',
    url='https://github.com/CIRCL/IP-ASN-history',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    maintainer_email='raphael.vinot@circl.lu',
    packages=['ipasn'],
    cmdclass = {'build_py': build_py},
    license='GNU GPLv3',
    long_description=open('README.md').read(),
    )
