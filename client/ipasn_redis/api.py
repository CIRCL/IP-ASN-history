#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis
try:
    from itertools import izip as zip
except ImportError:  # will be 3.x series
    pass


class IPASN(object):

    def __init__(self, socket=None, host=None, port=None, db=0, skip_exception=True):
        if not socket and not host:
            raise Exception('You need to provide at least a socket or a host')
        if socket:
            self.routing_db = redis.Redis(unix_socket_path=socket, db=db)
        else:
            self.routing_db = redis.Redis(host=host, port=port, db=db)
        self.db = db
        self.skip_exception = skip_exception
        self.update_dates()
        self.current_announce_date = self.default_announce_date
        self.netmasks = [[128, 0, 0, 0], [192, 0, 0, 0], [224, 0, 0, 0], [240, 0, 0, 0],
                         [248, 0, 0, 0], [252, 0, 0, 0], [254, 0, 0, 0], [255, 0, 0, 0],
                         [255, 128, 0, 0], [255, 192, 0, 0], [255, 224, 0, 0], [255, 240, 0, 0],
                         [255, 248, 0, 0], [255, 252, 0, 0], [255, 254, 0, 0], [255, 255, 0, 0],
                         [255, 255, 128, 0], [255, 255, 192, 0], [255, 255, 224, 0], [255, 255, 240, 0],
                         [255, 255, 248, 0], [255, 255, 252, 0], [255, 255, 254, 0], [255, 255, 255, 0],
                         [255, 255, 255, 128], [255, 255, 255, 192], [255, 255, 255, 224],
                         [255, 255, 255, 240], [255, 255, 255, 248], [255, 255, 255, 252]]

    def update_dates(self):
        self.number_of_days = self.routing_db.scard('imported_dates')
        self.default_announce_date = sorted(self.routing_db.smembers('imported_dates'), reverse=True)[0]

    def prepare_keys(self, ip):
        keys = [ip + '/32']
        try:
            ip_split = [int(digit) for digit in ip.split('.')]
            ziped = zip([zip(ip_split, m) for m in reversed(self.netmasks)], range(30, 0, -1))
            keys += ['{}.{}.{}.{}/{mask}'.format(mask=mask, *[x & z for x, z in val]) for val, mask in ziped]
        except Exception as e:
            if not self.skip_exception:
                raise e
        return keys

    def get_current_date(self):
        """
            Return the date the query has been using.

            :rtype: String, date, Format: YYYY-MM-DD
        """
        return self.current_announce_date

    def get_announce_date(self, announce_date):
        if announce_date is None:
            self.update_dates()
            announce_date = self.default_announce_date
        elif not self.routing_db.sismember('imported_dates', announce_date):
            dates = self.routing_db.smembers('imported_dates')
            try:
                announce_date = min(enumerate(dates), key=lambda x: abs(int(x[1]) - int(announce_date)))[1]
            except:
                announce_date = self.default_announce_date
            if not self.skip_exception:
                raise Exception("unknown date")
        return announce_date

    def run(self, ip, announce_date=None):
        announce_date = self.get_announce_date(announce_date)
        keys = self.prepare_keys(ip)
        p = self.routing_db.pipeline(False)
        [p.hget(k, announce_date) for k in keys]
        return p.execute(), announce_date, keys

    def asn(self, ip, announce_date=None):
        """
            Give an IP, maybe a date, get the ASN.
            This is the fastest command.

            :param ip: IP address to search for
            :param announce_date: Date of the announcement

            :rtype: String, ASN.

        """
        assignations, announce_date, _ = self.run(ip, announce_date)
        return next((assign for assign in assignations if assign is not None), None), announce_date

    def date_asn_block(self, ip, announce_date=None):
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
        assignations, announce_date, keys = self.run(ip, announce_date)
        pos = next((i for i, j in enumerate(assignations) if j is not None), None)
        if pos is not None:
            block = keys[pos]
            if block != '0.0.0.0/0':
                return announce_date, assignations[pos], block
        return None

    def history(self, ip, days_limit=None):
        """
            Get the full history of an IP. It takes time.

            :param ip: IP address to search for
            :param days_limit: Max amount of days to query. (None means no limit)

            :rtype: list. For each day in the database: day, asn, block
        """
        all_dates = sorted(self.routing_db.smembers('imported_dates'), reverse=True)
        if days_limit is not None:
            all_dates = all_dates[:days_limit]
        return [self.date_asn_block(ip, date) for date in all_dates]

    def aggregate_history(self, ip, days_limit=None):
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
        for entry in self.history(ip, days_limit):
            if entry is None:
                continue
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
