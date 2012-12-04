#!/usr/bin/python
# -*- coding: utf-8 -*-

# Usage: cat <file> | python client.py
# Example line of the input file: 127.0.0.1 20130101
# Note: the last parameter (the day) is optional,
#       the default value is the last imported day
# The output of the script is: 127.0.0.1 3303 20130101

import redis
import itertools
import sys

if  sys.version_info[0] == 3:
    # itertools.izip does not exists in python 3 and is much faster in python 2
    itertools.izip = zip

use_unix_socket = True

hostname = '127.0.0.1'
port = 6379
redis_db = 0

skip_exception = True

ready = False
default_announce_date = None

routing_db = None
keys = []

netmasks = [ [128, 0, 0, 0],
             [192, 0, 0, 0],
             [224, 0, 0, 0],
             [240, 0, 0, 0],
             [248, 0, 0, 0],
             [252, 0, 0, 0],
             [254, 0, 0, 0],
             [255, 0, 0, 0],
             [255, 128, 0, 0],
             [255, 192, 0, 0],
             [255, 224, 0, 0],
             [255, 240, 0, 0],
             [255, 248, 0, 0],
             [255, 252, 0, 0],
             [255, 254, 0, 0],
             [255, 255, 0, 0],
             [255, 255, 128, 0],
             [255, 255, 192, 0],
             [255, 255, 224, 0],
             [255, 255, 240, 0],
             [255, 255, 248, 0],
             [255, 255, 252, 0],
             [255, 255, 254, 0],
             [255, 255, 255, 0],
             [255, 255, 255, 128],
             [255, 255, 255, 192],
             [255, 255, 255, 224],
             [255, 255, 255, 240],
             [255, 255, 255, 248],
             [255, 255, 255, 252]]


def prepare():
    global routing_db
    global ready
    global default_announce_date
    if use_unix_socket:
        routing_db = redis.Redis(unix_socket_path='/tmp/redis.sock', db=redis_db)
    else:
        routing_db = redis.Redis(host = hostname, port=port, db=redis_db)
    default_announce_date = sorted(routing_db.smembers('imported_dates'),
            reverse = True)[0]
    ready = True

def prepare_keys(ip):
    global keys
    if not ready:
        prepare()
    try:
        keys = [ip +'/32']
        ip_split = [int(digit) for digit in ip.split('.')]
        for mask in reversed(list(range(30))):
            tmpip = [str(a & b) for a, b in itertools.izip(ip_split, netmasks[mask])]
            keys.append('.'.join(tmpip) + '/' + str(mask + 1))
    except Exception as e:
        keys = []
        if not skip_exception:
            raise e

def run(announce_date = None):
    p = routing_db.pipeline(False)
    if announce_date is None:
        announce_date = default_announce_date
    [p.hget(k, announce_date) for k in keys]
    return p.execute()

def asn(announce_date = None):
    assignations = run(announce_date)
    return next((assign for assign in assignations
        if assign is not None), None)

def date_asn_block(announce_date = None):
    assignations = run(announce_date)
    pos = next((i for i, j in enumerate(assignations) if j is not None), None)
    if pos is not None:
        block = keys[pos]
        if block != '0.0.0.0/0':
            asn = assignations[pos]
            return announce_date, asn, block
    return None

def history():
    all_dates = sorted(routing_db.smembers('imported_dates'), reverse = True)
    for date in all_dates:
        yield date_asn_block(date)

