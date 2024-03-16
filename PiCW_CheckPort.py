#!/usr/bin/python3

# PiCW_CheckPort.py
#   - a port monitoring daemon for TX control

import time
import sys
import InputPort as inPort
import KeyingControl   as key
import StraightKeyer   as stk

# disable responses for all input ports
#
inPort.bind(inPort.In_A, stk.null_action)
inPort.bind(inPort.In_B, stk.null_action)
inPort.bind(inPort.In_C, stk.null_action)

# monitoring TX control port
# for maxcount*interval seconds
#
# If TX control port being
# activated whole continuously,
# deactivate the port.

interval=1

# sync to timeout of sendable_dots
maxcount=max(int(key.sendable_dots*key.dotlen*2/interval), 1)

count=0
while True:
    for i in (range(maxcount)):
        time.sleep(interval)
        stat=inPort.check_port(port.Out_T)
        if stat==1:
            count += 1
            if maxcount<=count:
                key.space()
                count=0
        else:
            count=0
        sys.stdout.write(str(stat))
        sys.stdout.flush()
    print(' : {:2d}'.format(count))
