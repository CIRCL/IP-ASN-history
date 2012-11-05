IP-ASN-history
==============

IP-ASN-history is a tool to query an IP address to get the ASN history of the announce.

1.  Prerequired

    You will need this:
        * Redis server with unix socket enabled
        * Binaries:
            - get the latest bgpdump from http://www.ris.ripe.net/source/bgpdump/
            - build it and copy bgpdump in server/bin/
        * Python libraries:
            - redis-py: https://github.com/andymccurdy/redis-py/
            - IPy: https://github.com/haypo/python-ipy
            - pubsublogger: https://github.com/Rafiot/PubSubLogger
            - logbook: http://packages.python.org/Logbook/ (only if you want to log)

2.  Populate the database

    You can import all the dumps in bgpdump format but the source is not saved in
    the database. The best way to import announcement of ifferent soures is to use
    different redis databases.

    ```bash
    cd server
    ./fetch_historical_bviews.py -f YYYY-MM-DD # date of the oldest file to download
    ./db_generator.py
    ```

    Note: fetch_historical_bviews.py and db_generator.py are services, do not start them in a cron.

    Optional: Run ./start_logging.sh if you want to log the import.
    The logfiles will be in server/logs/

3.  Query the database

    Have a look at client/

    Change the IP and the port in ip_asn_history/api.py if necessary.

    To install the library system-wide:

    ```bash
    cd client
    python setup.py install
    ```
