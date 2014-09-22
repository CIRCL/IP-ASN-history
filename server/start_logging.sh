#!/bin/bash

log_subscriber --channel bview --log_path logs/ -H 127.0.0.1 -p 16379 &
log_subscriber --channel bviewfetch --log_path logs/ -H 127.0.0.1 -p 16379 &
log_subscriber --channel bviewparse --log_path logs/ -H 127.0.0.1 -p 16379 &
