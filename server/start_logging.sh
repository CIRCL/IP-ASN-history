#!/bin/bash

log_subscriber --channel bview --log_path logs/ &
log_subscriber --channel bviewfetch --log_path logs/ &
log_subscriber --channel bviewparse --log_path logs/ &
