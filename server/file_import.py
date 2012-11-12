#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/pushing_process.py` - Push RIS
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Service pushing the routing information.

    This service runs on a file and extract from each RI block the network and the ASN
    announcing this block. Both of them are pushed into the redis database.

"""
import os
import redis
import re

from pubsublogger import publisher
import argparse

routing_db = redis.Redis(unix_socket_path='/tmp/redis.sock')


def db_import(filename, day):
    with open(filename, 'r') as f:
        entry = ''
        pipeline = routing_db.pipeline()
        i = 0
        for line in f:
            # End of block, extracting the information
            if line == '\n':
                i += 1
                parsed = re.findall('(?:ASPATH|PREFIX): ([^\n{]*)', entry)
                try:
                    block = parsed[0].strip()
                    # RIPE-NCC-RIS BGP IPv6 Anchor Prefix @RRC00
                    # RIPE-NCC-RIS BGP Anchor Prefix @ rrc00 - RIPE NCC
                    if block in ['2001:7fb:ff00::/48', '84.205.80.0/24',
                            '2001:7fb:fe00::/48', '84.205.64.0/24']:
                        asn = 12654
                    else:
                        asn = int(parsed[1].split()[-1].strip())
                    pipeline.hset(block, day, asn)
                except:
                    #FIXME: check the cause of the exception
                    publisher.warning(entry)
                entry = ''
                if i%10000 == 0:
                    pipeline.execute()
                    pipeline = routing_db.pipeline()
            else :
                # append the line to the current block.
                entry += line
        pipeline.execute()
        publisher.info('{f} finished, {nb} entries impported.'.\
                format(f=filename, nb = i))

if __name__ == '__main__':

    publisher.channel = 'bviewparse'
    publisher.use_tcp_socket = False

    parser = argparse.ArgumentParser(description='Parse a bview file.')
    parser.add_argument("-f", "--filename", required=True, type=str,
            help='Name of the file.')
    parser.add_argument("-d", "--day", required=True, type=str,
            help='Day of the dump: YYYYMMDD')
    args = parser.parse_args()

    day = int(args.day)

    db_import(args.filename, day)

    os.unlink(args.filename)
