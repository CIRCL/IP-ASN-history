#!/usr/bin/env python
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
import urllib
import time

import httplib
from urlparse import urlparse

from pubsublogger import publisher
import constraints as c


sleep_timer = 3600
base_url = 'http://data.ris.ripe.net/rrc00/{year_month}/bview.{file_day}.{hour}.gz'
hours = ['0000', '0800', '1600']
path_temp_bviewfile = os.path.join(c.bview_dir, 'tmp', 'bview.gz')
current_date = None


def checkURL(url):
    """
        Check if the URL exists by getting the header of the response.
    """
    p = urlparse(url)
    h = httplib.HTTPConnection(p[1])
    h.request('HEAD', p[2])
    reply = h.getresponse()
    h.close()
    if reply.status == 200:
        return 1
    else:
        return 0


def downloadURL(url):
    """
        Inconditianilly download the URL in a temporary directory.
        When finished, the file is moved in the real directory.
        Like this an other process will not attempt to extract an inclomplete file.
    """
    urllib.urlretrieve(url, os.path.join(c.raw_data, path_temp_bviewfile))
    os.rename(os.path.join(c.raw_data, path_temp_bviewfile), c.path_bviewfile)


def already_downloaded(date, hour):
    """
        Verify that the date and the hour of the file we try to
        download is newer than the latest downloaded file.
    """
    if os.path.exists(c.path_bviewtimesamp):
        ts = open(c.path_bviewtimesamp, 'r').read().split()
        if ts[0] == date:
            if int(ts[1]) >= int(hour):
                return True
    open(c.path_bviewtimesamp, 'w').write(date + ' ' + hour)
    return False


if __name__ == '__main__':

    publisher.channel = 'bviewfetch'

    while 1:
        try:
            current_date = datetime.date.today()
            # Initialization of the URL to fetch
            year_month = current_date.strftime("%Y.%m")
            file_day = current_date.strftime("%Y%m%d")

            for hour in reversed(hours):
                url = base_url.format(year_month=year_month,
                                      file_day=file_day, hour=hour)
                if checkURL(url):
                    if not already_downloaded(file_day, hour):
                        publisher.info("New bview file found: " + url)
                        downloadURL(url)
                        publisher.info("Downloaded.")
                        last_hour = hour
                        break
        except:
            publisher.critical('Unable to download bview file. Server does not respond.')
        time.sleep(sleep_timer)
