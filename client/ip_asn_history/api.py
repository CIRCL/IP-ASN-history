#!/usr/bin/python
# -*- coding: utf-8 -*-

# Usage: cat <file> | python client.py
# Example line of the input file: 127.0.0.1 20130101
# Note: the last parameter (the day) is optional,
#       the default value is the last imported day
# The output of the script is: 127.0.0.1 3303 20130101


import IPy
import redis
import struct
import socket

redis_db = 0

redis_use_socket = True

redis_host = '127.0.0.1'
redis_port = 6379


ip = None
ready = False
default_announce_date = None

routing_db = None
keys = []

netmasks = ['30', '29', '28', '27', '26', '25', '24', '23',
            '22', '21', '20', '19', '18', '17', '16', '15',
            '14', '13', '12', '11', '10', '9', '8', '7', '6',
            '5', '4', '3', '2', '1', '0']

def prepare():
    global routing_db
    global ready
    global default_announce_date
    if redis_use_socket:
        routing_db = redis.Redis(unix_socket_path='/tmp/redis.sock', db=redis_db)
    else:
        routing_db = redis.Redis(port=redis_port, db=redis_db)
    default_announce_date = sorted(routing_db.smembers('imported_dates'), reverse = True)[0]
    ready = True


def prepare_keys(ip):
    global keys
    _ip = struct.unpack('!I', socket.inet_aton(ip))[0]
    keys = [ '/'.join([socket.inet_ntop(socket.AF_INET,
                struct.pack('!I', IPy.IP('/'.join([hex(_ip), nm]),
                    make_net = True).int())), nm]) for nm in netmasks]
    keys.insert(0, ip +'/32')

def run(announce_date = None):
    if not ready:
        prepare()
    p = routing_db.pipeline(False)
    if announce_date is None:
        announce_date = default_announce_date
    [p.hget(k, announce_date) for k in keys]
    return p.execute()

def asn_date(announce_date = None):
    assignations = run(announce_date)
    return next((assign for assign in assignations
        if assign is not None), None)

def history():
    if not ready:
        prepare()
    all_dates = sorted(routing_db.smembers('imported_dates'), reverse = True)
    for date in all_dates:
        assignations = run(date)
        pos = next((i for i, j in enumerate(assignations) if j is not None), None)
        block = keys[pos]
        asn = assignations[pos]
        if pos is not None and block != '0.0.0.0/0':
            yield date, asn, block
        else:
            yield None

