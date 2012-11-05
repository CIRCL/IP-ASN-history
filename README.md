IP-ASN-history
==============

IP-ASN-history is a tool to lookup the ASN which announce an IP over the time.

0. Prerequired

* Redis server
* Binaries:
    - latest bgpdump in server/bin/ (Available here: http://www.ris.ripe.net/source/bgpdump/)
* Python libraries:
    - redis-py: https://github.com/andymccurdy/redis-py/
    - pubsublogger: https://github.com/Rafiot/PubSubLogger
    - logbook: http://packages.python.org/Logbook/ (only if you want to log)

1. Populate the database

You can import all the dumps in bgpdump format but the source is not saved in
the database. The best way to import announcement of ifferent soures is to use
different redis databases.

```bash
cd server
./fetch_historical_bviews.py -f YYYY-MM-DD # date of the oldest file to download
./db_generator.py
```

Optional: Run ./start_logging.sh if you want to log the import.
The logfiles will be in server/logs/

2. Query the database

Have a look at client/

Change the IP and the port in ip_asn_history/api.py if necessary.

To install the library system-wide:

```bash
cd cient
python setup.py install
```
