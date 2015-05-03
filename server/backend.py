#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import redis
import os


def get_redis_connector():
    configfile = os.path.join('config.cfg')
    if not os.path.exists(configfile):
        raise Exception('Unable to find the configuration file.')
    config = configparser.ConfigParser()
    config.read(configfile)
    section_name = config.get('General', 'backend')
    if not config.has_section(section_name):
        raise Exception('Invalid section name.')
    if config.has_option(section_name, 'sock'):
        return redis.StrictRedis(
            unix_socket_path=config.get(section_name, 'sock'))
    else:
        return redis.StrictRedis(
            host=config.get(section_name, 'hostname'),
            port=config.get(section_name, 'port'),
            db=config.get(section_name, 'db'))
