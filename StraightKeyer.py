# StraightKeyer - logic for a straight key

import InputPort as inPort
import KeyingControl   as key

pressing=False
actstat=False  # current status

# callback function
#
def action(state):
    global pressing

    # almost pass-through
    #
    if state==key.PRESSED:
        key.mark()
        key.abort_request() # request to abort text keyer
        pressing=True
    elif state==key.RELEASED:
        key.space()
        pressing=False

# callback function to do nothing
#
def null_action(state):
    if state==key.PRESSED:
        key.abort_request()


# initialization
#
def getaction():
    return actstat

def setaction(newact):
    global actstat

    if actstat != newact:
        actstat = not not newact
        if actstat:
            inPort.bind(inPort.In_C, action)
        else:
            inPort.bind(inPort.In_C, null_action)
