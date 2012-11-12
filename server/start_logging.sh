#!/bin/bash

log_subscriber -s --channel bview --log_path logs/ &
log_subscriber -s --channel bviewfetch --log_path logs/ &
log_subscriber -s --channel bviewparse --log_path logs/ &
