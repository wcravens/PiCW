#!/usr/bin/python3

# PiCW.py - Morse Code Keyer using GPIO of Raspberry Pi
#
#   Yoshihiro Kawamata
#       (kaw@on.rim.or.jp, ex JH0NUQ)

import os.path
import InputPort as inPort
import OutputPort as outPort
import DualPoleKeyer     as dual_pole_keyer
import CwUtilities     as cw_utils
import MemoryKeyer     as memory_keyer
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


dual_pole_keyer.settype('IAMBIC')
dual_pole_keyer.initialize()
dual_pole_keyer.straight_key.set_enabled(True)

# command console
#
while True:
    # read user's input
    #
    try:
        line=input("\n"+cw_utils.speedstr()+\
                   ('/REC' if memory_keyer.recording else '')+\
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
dual_pole_keyer.terminate()
outPort.terminate()
print()
print("Bye bye...")
