#!/bin/python
# -*- coding: utf-8 -*-

"""
This is a python implementation to simplify the use of the JSON API.
It allows an access to all the functions of the Redis API, via the network.

The parameters are as consistent as possible with the Redis API.

"""

try:
    import simplejson as json
except:
    import json

import requests

url = 'http://bgpranking.circl.lu/ipasn'

def __prepare_request(query):
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(query), headers=headers)
    return r.json()

def asn(ip, announce_date = None):
    query = {'method': 'asn'}
    query.update({'ip': ip, 'announce_date': announce_date})
    return __prepare_request(query)

def date_asn_block(ip, announce_date = None):
    query = {'method': 'date_asn_block'}
    query.update({'ip': ip, 'announce_date': announce_date})
    return __prepare_request(query)

def history(ip, days_limit = None):
    query = {'method': 'history'}
    query.update({'ip': ip, 'days_limit': days_limit})
    return __prepare_request(query)

def aggregate_history(ip, days_limit = None):
    query = {'method': 'aggregate_history'}
    query.update({'ip': ip, 'days_limit': days_limit})
    return __prepare_request(query)

