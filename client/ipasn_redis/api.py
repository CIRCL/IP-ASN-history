#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import itertools
import sys

if  sys.version_info[0] == 3:
    # itertools.izip does not exists in python 3 and is much faster in python 2
    itertools.izip = zip

use_unix_socket = False

hostname = '127.0.0.1'
port = 6382
redis_db = 0

skip_exception = True

__current_announce_date = None
__default_announce_date = None
__number_of_days = -1
__routing_db = None
__keys = []
__netmasks = [ [128, 0, 0, 0],
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


def __prepare():
    global __routing_db
    if use_unix_socket:
        __routing_db = redis.Redis(unix_socket_path='/tmp/redis.sock', db=redis_db)
    else:
        __routing_db = redis.Redis(host = hostname, port=port, db=redis_db)
    __update_default_announce_date()

def __update_default_announce_date():
    global __default_announce_date
    global __number_of_days
    new_number_of_days = __routing_db.scard('imported_dates')
    if new_number_of_days != __number_of_days:
        __number_of_days = new_number_of_days
        dates = sorted(__routing_db.smembers('imported_dates'), reverse=True)
        if len(dates) > 0:
            __default_announce_date = dates[0]

def __prepare_keys(ip):
    global __keys
    try:
        __keys = [ip +'/32']
        ip_split = [int(digit) for digit in ip.split('.')]
        for mask in reversed(list(range(30))):
            tmpip = [str(a & b) for a, b in
                    itertools.izip(ip_split, __netmasks[mask])]
            __keys.append('.'.join(tmpip) + '/' + str(mask + 1))
    except Exception as e:
        __keys = []
        if not skip_exception:
            raise e

def get_current_date():
    """
        Return the date the query has been using.

        :rtype: String, date, Format: YYYY-MM-DD
    """
    return __current_announce_date

def __run(ip, announce_date = None):
    global __current_announce_date
    if announce_date is None:
        __update_default_announce_date()
        __current_announce_date = __default_announce_date
    elif not __routing_db.sismember('imported_dates', announce_date):
        dates = __routing_db.smembers('imported_dates')
        try:
            __current_announce_date = min(enumerate(dates),
                    key=lambda x: abs(int(x[1])-int(announce_date)))[1]
        except:
            __current_announce_date = __default_announce_date
        if not skip_exception:
            raise Exception("unknown date")
    else:
        __current_announce_date = announce_date
    __prepare_keys(ip)
    p = __routing_db.pipeline(False)
    [p.hget(k, __current_announce_date) for k in __keys]
    return p.execute()

def asn(ip, announce_date = None):
    """
        Give an IP, maybe a date, get the ASN.
        This is the fastest command.

        :param ip: IP address to search for
        :param announce_date: Date of the announcement

        :rtype: String, ASN.

    """
    assignations = __run(ip, announce_date)
    return next((assign for assign in assignations
        if assign is not None), None)

def date_asn_block(ip, announce_date = None):
    """
        Get the ASN and the IP Block announcing the IP at a specific date.

        :param ip: IP address to search for
        :param announce_date: Date of the announcement

        :rtype: tuple

            .. code-block:: python

                (announce_date, asn, block)

        .. note::

            the returned announce_date might be different of the one
            given in parameter because some raw files are missing and we
            don't have the information. In this case, the nearest known
            date will be chosen,
    """
    assignations = __run(ip, announce_date)
    pos = next((i for i, j in enumerate(assignations) if j is not None), None)
    if pos is not None:
        block = __keys[pos]
        if block != '0.0.0.0/0':
            asn = assignations[pos]
            return __current_announce_date, asn, block
    return None

def history(ip, days_limit=None):
    """
        Get the full history of an IP. It takes time.

        :param ip: IP address to search for
        :param days_limit: Max amount of days to query. (None means no limit)

        :rtype: list. For each day in the database: day, asn, block
    """
    all_dates = sorted(__routing_db.smembers('imported_dates'), reverse = True)
    if days_limit is not None:
        all_dates = all_dates[:days_limit]
    for date in all_dates:
        yield date_asn_block(ip, date)

def aggregate_history(ip, days_limit=None):
    """
        Get the full history of an IP, aggregate the result instead of
        returning one line per day.

        :param ip: IP address to search for
        :param days_limit: Max amount of days to query. (None means no limit)

        :rtype: list. For each change: FirstDay, LastDay, ASN, Block
    """
    first_date = None
    last_date = None
    prec_asn = None
    prec_block = None
    for entry in history(ip, days_limit):
        if entry is not None:
            date, asn, block = entry
            if first_date is None:
                last_date = date
                first_date = date
                prec_asn = asn
                prec_block = block
            elif prec_asn == asn and prec_block == block:
                first_date = date
            else:
                yield first_date, last_date, prec_asn, prec_block
                last_date = date
                first_date = date
                prec_asn = asn
                prec_block = block
    if first_date is not None:
        yield first_date, last_date, prec_asn, prec_block

