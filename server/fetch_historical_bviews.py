#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    :file:`bin/services/fetch_bview.py` - Fetch the bview files
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The service fetch a dump of the routing database from
    the RIS Whois service provided by RIPE NCC.

    It verifies if the new file is more recent than the one already downloaded.
    When the script is started, the most recent dump is inconditionally downloaded.

    The URL to download looks like that:

        ::

            http://data.ris.ripe.net/rrc00/YYYY.MM/bview.YYYYMMDD.HHHH.gz
            YYYY    = Year (e.g. 2010)
            MM      = Month (e.g. 09)
            DD      = Day (e.g. 01)
            HHHH    = Hour (0000, 0800 or 1600)

    We always want to fetch the latest available dump, the script will take
    the current day and try to find a file corresponding to one of the three possible hours,
    in reverse order.

    If the script is not restarted, it will never download two time the same file:
    the hour corresponding the last downloaded file is saved.

    .. note::
        When the current day change, this hour is set to None.

    To verify if the URL to fetch exists, we use a function provided by the two following links
     - http://code.activestate.com/recipes/101276/ and
     - http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists

"""

import os
import datetime
from dateutil.parser import parse
import urllib
import argparse
import time

from pubsublogger import publisher
import constraints as c

# Format: YYYY-MM-DD
interval_first = None
interval_last = None

base_url = 'http://data.ris.ripe.net/rrc00/{year_month}/bview.{file_day}.0000.gz'
filename = 'bview.{day}.gz'

def check_dirs():
    main_dir = c.bview_dir
    tmp_dir = os.path.join(c.bview_dir, 'tmp')
    old_dir = os.path.join(c.bview_dir, 'old')
    if not os.path.exists(main_dir):
        os.mkdir(main_dir)
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    if not os.path.exists(old_dir):
        os.mkdir(old_dir)

def downloadURL(url, filename):
    """
        Inconditianilly download the URL in a temporary directory.
        When finished, the file is moved in the real directory.
        Like this an other process will not attempt to extract an inclomplete file.
    """
    path_temp_bviewfile = os.path.join(c.raw_data, c.bview_dir, 'tmp', filename)
    path_bviewfile = os.path.join(c.raw_data, c.bview_dir, filename)
    try:
        f = urllib.urlopen(url)
    except:
        return False
    if f.getcode() != 200:
        publisher.warning('{} unavailable, code: {}'.format(url, f.getcode()))
        return False
    with open(path_temp_bviewfile, 'w') as outfile:
        outfile.write(f.read())
    os.rename(path_temp_bviewfile, path_bviewfile)
    return True

def already_downloaded(filename):
    """
        Verify that the file has not already been downloaded.
    """
    cur_file = os.path.join(c.bview_dir, filename)
    old_file = os.path.join(c.bview_dir, 'old', filename)
    if not os.path.exists(cur_file) and not os.path.exists(old_file):
        return False
    return True

def to_download():
    """
        Build interval of urls to download.
        We always get the first file of the next day.
        Ex: 2013-01-01 => 2013-01-02.0000
    """
    first_day = parse(interval_first)
    last_day = parse(interval_last)
    one_day = datetime.timedelta(1)
    cur_day = first_day
    url_list = []
    while cur_day < last_day:
        fname = filename.format(day = cur_day.strftime("%Y%m%d"))
        cur_day += one_day
        url = base_url.format(year_month = cur_day.strftime("%Y.%m"),
                file_day = cur_day.strftime("%Y%m%d"))
        url_list.append((fname, url))
    return sorted(url_list, key=lambda tup: tup[0], reverse=True)


if __name__ == '__main__':
    check_dirs()
    publisher.channel = 'bviewfetch'
    publisher.use_tcp_socket = False

    parser = argparse.ArgumentParser(description='Fetch all the bview files of an interval.')
    parser.add_argument("-f", "--firstdate", required=True, type=str,
            help='First date of the interval [YYYY-MM-DD].')
    parser.add_argument("-l", "--lastdate", type=str, default=None,
            help='Last date of the interval [YYYY-MM-DD].')

    args = parser.parse_args()
    interval_first = args.firstdate
    interval_last = args.lastdate
    if interval_last is None:
        daemon = True
    else:
        daemon = False

    unavailable = []
    while 1:
        got_new_files = False
        if daemon or interval_last is None:
            interval_last = datetime.date.today().strftime("%Y-%m-%d")

        for fname, url in to_download():
            if not already_downloaded(fname) and url not in unavailable:
                publisher.debug("Trying to download: " + url)
                if downloadURL(url, fname):
                    got_new_files = True
                    publisher.info("Downloaded:" + fname)
                elif interval_last != datetime.date.today().strftime("%Y-%m-%d"):
                    # if today's file is not available, try again later.
                    unavailable.append(url)
        if not got_new_files:
            publisher.info('No new files to download.')
            if not daemon:
                publisher.info('Exiting...')
                break
            time.sleep(3600)
