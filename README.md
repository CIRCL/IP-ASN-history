IP-ASN-history
==============

IP-ASN-history is a server software to store efficiently the history
of BGP announces and quickly lookup IP addresses origins. The server
is supporting bgpdump format for importing BGP announces (e.g. from RIPE RIS dump
or your own openbgpd dump file).

1.  Prerequired

    You will need this:

    * Redis server with unix socket enabled
    * Binaries:
        - get the latest bgpdump from http://www.ris.ripe.net/source/bgpdump/
        - build it and copy bgpdump in server/bin/
    * Python libraries:
        - redis-py: https://github.com/andymccurdy/redis-py/
        - dateutil: https://launchpad.net/dateutil
        - IPy: https://github.com/haypo/python-ipy
        - pubsublogger: https://github.com/Rafiot/PubSubLogger
        - logbook: http://packages.python.org/Logbook/ (only if you want to log)

2.  Populate the database

    You can import all the dumps in bgpdump format but the original is not saved in
    the database. The best way to import announcement of different sources is to use
    different redis databases.

    ```bash
    cd server
    ./fetch_historical_bviews.py -f YYYY-MM-DD # date of the oldest file to download
    ./db_generator.py
    ```

    Note: fetch_historical_bviews.py and db_generator.py are services, do not start them in a cron.

    Optional: Run ./start_logging.sh if you want to log the import process.

    The log files are located in the server/logs/ directory.

3.  Query the database

    Client software is located in the directory client.

    Change the IP and the port in ip_asn_history/api.py if necessary.

    You can query any IP addresses to get the full history:

    ```bash
    cd client
    python ip2asn_fullhistory -i 8.8.8.8
    20121104 15169 8.8.8.0/24
    20121103 15169 8.8.8.0/24
    20121102 15169 8.8.8.0/24
    20121101 15169 8.8.8.0/24
    ```

    To install the library system-wide:

    ```bash
    cd client
    python setup.py install
    ```

    Note: By default, if the IP is invalid, it is simply skipped. If you want
    to see the exceptions, enable the debug flag (-d) or set the variable
    "skip_exception" to False in the API.

License
-------

IP-ASN-history is licensed under the GNU Affero License version 3 or upper.
