#!/usr/bin/python3

# PiCW.py - Morse Code Keyer using GPIO of Raspberry Pi
#
#   Yoshihiro Kawamata
#       (kaw@on.rim.or.jp, ex JH0NUQ)

import os.path
import InputPort as inPort
import OutputPort as outPort
import PaddleKeyer     as pdl
import CwUtilities     as utl
import MemoryKeyer     as mem
import ConsoleCommands as cmd

print("Welcome to PiCW.py")
print("  '?'   for the short help.")
print("  <TAB> for command completion.")

# load initial configuration file
#
initfile=os.path.expanduser('~/.picwrc')
try:
    if os.path.exists(initfile):
        print()
        cmd.load_file(initfile)
except:
    pass


inPort.initialize_input_ports()
outPort.initialize_output_ports()
outPort.set_beepfreq( 800 )


pdl.settype('IAMBIC')
pdl.initialize()
pdl.straight_key.set_enabled(True)

# command console
#
while True:
    # read user's input
    #
    try:
        line=input("\n"+utl.speedstr()+\
                   ('/REC' if mem.recording else '')+\
                   ':')
        print()
    except KeyboardInterrupt:
        continue
    except EOFError:
        break

    if not cmd.parser(line):
        break

# termination processes
#
pdl.terminate()
outPort.terminate()
print()
print("Bye bye...")
