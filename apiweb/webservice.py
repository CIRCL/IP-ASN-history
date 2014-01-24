#!/bin/python
# -*- coding: utf-8 -*-

"""
The JSON API allows to do queries the IP ASN History database.

By default, the path where the webservice is listening is
http://domain/json

You need to send a well-formed JSON object with a entry 'method' and as
value the name of the function you want to call (listed bellow).

The other entries of the JSON Object will depend on the function. To keep
it simple, the name of each entry is the parameter name from the Redis API.

"""


from flask import Flask, json, request
import StringIO
import csv

import ipasn_redis as ipasn
ipasn.hostname='127.0.0.1'
ipasn.port=6390

logging = True

try:
    if logging:
        from pubsublogger import publisher
        publisher.channel = 'IPASN_Web'
        publisher.port = 6390
except:
    logging = False


app = Flask(__name__)
app.debug = False

authorized_methods = ['asn', 'date_asn_block', 'history', 'aggregate_history']

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) == type(set()):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

def __csv2string(data):
    si = StringIO.StringIO();
    cw = csv.writer(si);
    cw.writerow(data);
    return si.getvalue().strip('\r\n');


def __query_logging(ip, user_agent, method, q_ip=None, announce_date=None,
        days_limit=None, level=None):
    if level == 'warning':
        publisher.warning(__csv2string([ip, user_agent, method, q_ip,
            announce_date, days_limit, level]))
    elif level == 'error':
        publisher.error(__csv2string([ip, user_agent, method, q_ip,
            announce_date, days_limit, level]))
    else:
        publisher.info(__csv2string([ip, user_agent, method, q_ip,
            announce_date, days_limit, level]))


@app.route('/json', methods = ['POST'])
def __entry_point():
    """
        Function called when an query is made on /json. Expects a JSON
        object with at least a 'method' entry.
    """
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', 'Empty User-Agent')
    method = request.json.get('method')
    if method is None:
        __query_logging(ip, ua, method, level = 'warning')
        return json.dumps({'error': 'No method provided.'})
    if method not in authorized_methods:
        # unauthorized query
        __query_logging(ip, ua, method, level = 'warning')
        return json.dumps({'error': 'Unauthorized method.'})
    fct = globals().get(method)
    if fct is None:
        # unknown method, the method is authorized, but does not exists...
        __query_logging(ip, ua, method, level = 'warning')
        return json.dumps({'error': 'Unknown method.'})
    if request.json.get('ip') is None:
        __query_logging(ip, ua, method, level = 'warning')
        return json.dumps({'error': 'No IP provided, not going to work.'})
    try:
        result = fct(request.json)
        __query_logging(ip, ua, method, request.json.get('ip'),
                request.json.get('announce_date'), request.json.get('days_limit'))
        return result
    except Exception as e:
        __query_logging(ip, ua, method, request.json.get('ip'), level = 'error')
        return json.dumps({'error': 'Something went wrong.'})

def asn(request):
    ip = request.get('ip')
    if ip is None:
         return json.dumps({})
    return json.dumps(ipasn.asn(ip, request.get('announce_date')))

def date_asn_block(request):
    ip = request.get('ip')
    if ip is None:
         return json.dumps({})
    return json.dumps(ipasn.date_asn_block(ip,
        request.get('announce_date')))

def history(request):
    ip = request.get('ip')
    if ip is None:
         return json.dumps({})
    return json.dumps([(line[0], line[1], line[2]) for line in
        ipasn.history(ip, request.get('days_limit') or 30) if line is not None])

def aggregate_history(request):
    ip = request.get('ip')
    if ip is None:
         return json.dumps({})
    return json.dumps([(line[0], line[1], line[2], line[3])
        for line in ipasn.aggregate_history(ip, request.get('days_limit') or 30)
        if line is not None])

if __name__ == '__main__':
    app.run(host='0.0.0.0')
