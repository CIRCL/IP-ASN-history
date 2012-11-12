#!/usr/bin/python
# -*- coding: utf-8 -*-

import constraints as c

import subprocess
import signal
import os
from subprocess import Popen, PIPE
import time
import redis
import glob
import datetime



import file_splitter
from pubsublogger import publisher


simultaneous_db_import = 10
path_to_importer = os.path.join(os.curdir, 'file_import.py')

path_output_bviewfile = os.path.join(c.bview_dir, 'bview')
bview_check_interval = 3600
sleep_timer = 10
path_to_bgpdump_bin = os.path.join('bin', 'bgpdump')

key_to_rank = 'to_rank'
key_latest_ranking = 'latest_ranking'
key_amount_asns = 'amount_asns'
index_sources = 'sources'
index_asns_details = 'asns_details'

imported_day = 0

def service_start(service = None, param = None):
    """
        Launch a Process, return his pid
    """
    if service is not None :
        to_run = ["python", service]
        if param is not None:
            to_run += param
        return subprocess.Popen(to_run)
    return False

def update_running_pids(old_procs):
    """
        Update the list of the running process and return the list
    """
    new_procs = []
    for proc in old_procs:
        if proc.poll() is None and check_pid(proc.pid):
            publisher.debug(str(proc.pid) + ' is alive')
            new_procs.append(proc)
        else:
            try:
                publisher.debug(str(proc.pid) + ' is gone')
                os.kill (proc.pid, signal.SIGKILL)
            except:
                # the process is just already gone
                pass
    return new_procs

def check_pid(pid):
    """
        Check For the existence of a unix pid.
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def run_splitted_processing(max_simultaneous_processes, process_name,
        filenames):
    """
        Run processes which push the routing dump of the RIPE in a redis database.
        The dump has been splitted in multiple files and each process run on one
        of this files.
    """
    pids = []
    while len(filenames) > 0:
        while len(filenames) > 0 and len(pids) < max_simultaneous_processes:
            filename = filenames.pop()
            pids.append(service_start(service = process_name,
                param = ['-f', filename, '-d', imported_day]))
        while len(pids) == max_simultaneous_processes:
            time.sleep(sleep_timer)
            pids = update_running_pids(pids)
    while len(pids) > 0:
        # Wait until all the processes are finished
        time.sleep(sleep_timer)
        pids = update_running_pids(pids)

def prepare_bview_file(filename):
    publisher.info('Start converting binary bview file in plain text...')
    # create the plain text dump from the binary dump
    with open(path_output_bviewfile, 'w') as output:
        nul_f = open(os.devnull, 'w')
        p_bgp = Popen([bgpdump , filename], stdout=PIPE, stderr = nul_f)
        for line in p_bgp.stdout:
            output.write(line)
        nul_f.close()
    publisher.info('Convertion finished, start splitting...')

    # Split the plain text file
    return file_splitter.fsplit(path_output_bviewfile)

def import_assignations(files):
    publisher.info('Start pushing all routes...')
    run_splitted_processing(simultaneous_db_import, path_to_importer, files)
    publisher.info('All routes pushed.')


if __name__ == '__main__':

    publisher.channel = 'bview'
    publisher.use_tcp_socket = False

    bgpdump = os.path.join(c.raw_data, path_to_bgpdump_bin)

    routing_db = redis.Redis(unix_socket_path='/tmp/redis.sock')

    # Wait a bit until the bview file is downloaded
    time.sleep(60)

    while 1:
        got_new_files = False
        files = glob.glob(os.path.join(c.bview_dir, 'bview.*.gz'))
        while len(files) > 0:
            files = sorted(files)
            f = files.pop()
            imported_day = os.path.basename(f).split('.')[1]
            if routing_db.sismember('imported_dates', imported_day):
                publisher.warning(f + ' as already been imported.')
                continue
            got_new_files = True
            time_begin = datetime.datetime.now()
            publisher.info('Importing ' + f)
            files = prepare_bview_file(f)
            import_assignations(files)
            routing_db.sadd('imported_dates', imported_day)
            publisher.info('Done with ' + f + '. Time: ' + str(datetime.datetime.now() - time_begin))

            # Remove the plain text file and move the binary
            os.unlink(path_output_bviewfile)
            os.rename(f, os.path.join(c.raw_data, c.bview_dir, 'old', os.path.basename(f)))
            files = glob.glob(os.path.join(c.bview_dir, 'bview.*.gz'))
        if not got_new_files:
            publisher.info('All the files availables have been imported...')
            time.sleep(3600)
