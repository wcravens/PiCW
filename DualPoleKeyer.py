# PaddleKeyer - logic for paddles with squeezing

import threading
import InputPort as inPort
import KeyingControl   as key
import SinglePoleKeyer   as straight_key
import CwUtilities     as utl

# states of a paddle
#
PADDLE_NONE=0 # unknown
PADDLE_DOT =1
PADDLE_DASH=2

# global status and notifying event
# for iambic paddles
#
pressing_dot =False  # current state of dot paddle. True when the paddle is being pressed.
pressing_dash=False  # current state of dash paddle.
paddle_event=PADDLE_NONE  # paddle invoked event
is_squeezed=PADDLE_NONE   # squeezed paddle while keying
iambic_thread_handle = None

# this event object is used to notify any paddle pressed
# from the iambic callback function
# to iambic keying subthread
#
ev_trigger=threading.Event()

# subthread for iambic output
#
def iambic_key_thread():

    # send dot or dash
    #
    def send(k):
        if k==PADDLE_DOT:
            key.dot()
            # If Straight key is also being pressed,
            # decrease speed
            if straight_key.pressing and tune_speed:
                key.setspeed(key.getspeed()-0.5)
                print('<', utl.speedstr(), '>', sep='')
        elif k==PADDLE_DASH:
            key.dash()
            # increase speed as of dot
            if straight_key.pressing and tune_speed:
                key.setspeed(key.getspeed()+0.5)
                print('<', utl.speedstr(), '>', sep='')

    # returns opposite paddle
    #
    def flip(k):
        if k==PADDLE_DOT:
            return PADDLE_DASH
        elif k==PADDLE_DASH:
            return PADDLE_DOT

    global ev_terminate
    ev_terminate=False

    global is_squeezed

    global modeB
    modeB=False  # default: mode A

    while True:
        # when idling,
        # wait for any paddle will be pressed
        ev_trigger.clear()
        ev_trigger.wait()
        key.abort_request() # request abort to message keyer

        if ev_terminate: # terminate this thread if requested
            return

        # sequences of keying
        #
        modeB_sqz=PADDLE_NONE  # first squeezed paddle of every event
        sendkey=paddle_event    # send by triggered paddle

        # send squeezed key
        #   or keep pressing
        #
        for i in range(key.sendable_dots):  # for fail-safe (60 sec max)
            is_squeezed=PADDLE_NONE  # possibly changed while calling send()
            send(sendkey)

            # send last dot/dash ?
            #
            if modeB \
               and modeB_sqz==PADDLE_NONE \
               and pressing_dot and pressing_dash:
                modeB_sqz=is_squeezed

            # determine next dot/dash
            #
            if not is_squeezed==PADDLE_NONE:  # squeezed. send it
                sendkey=is_squeezed

            # what to send, by status of pressing paddles
            #
            elif pressing_dot:
                if pressing_dash:  # pressing both
                    sendkey=flip(sendkey)
                else:              # pressing only dot
                    sendkey=PADDLE_DOT
            else:
                if pressing_dash:  # pressing only dash
                    sendkey=PADDLE_DASH
                else:              # pressing none
                    if modeB and not modeB_sqz==PADDLE_NONE:
                        send(flip(sendkey))
                    break

# callback function for iambic dot paddle
#
def dot_action(state):
    global pressing_dot, paddle_event, is_squeezed

    # paddle pressed
    if state==key.PRESSED:
        pressing_dot=True
        paddle_event=PADDLE_DOT
        if is_squeezed==PADDLE_NONE:
            is_squeezed=PADDLE_DOT
        ev_trigger.set() # notify to iambic subthread
    # paddle released
    elif state==key.RELEASED:
        pressing_dot=False
        paddle_event=PADDLE_NONE # ignore releasing

# callback function for iambic dash paddle
#
def dash_action(state):
    global pressing_dash, paddle_event, is_squeezed

    # paddle pressed
    if state==key.PRESSED:
        pressing_dash=True
        paddle_event=PADDLE_DASH
        if is_squeezed==PADDLE_NONE:
            is_squeezed=PADDLE_DASH
        ev_trigger.set() # notify to iambic subthread
    # paddle released
    elif state==key.RELEASED:
        pressing_dash=False
        paddle_event=PADDLE_NONE # ignore releasing

# property for every paddle type
#
#         paddle        ----------actions for-----------  Is speed
#         type          In_A             In_B             tunable?
typetab={'OFF':        [straight_key.null_action,   straight_key.null_action,   False   ],
         'IAMBIC':     [dot_action,                 dash_action,                True    ],
         'IAMBIC-REV': [dash_action,                dot_action,                 True    ],
         'BUG':        [dot_action,                 straight_key.action,        False   ],
         'BUG-REV':    [straight_key.action,        dot_action,                 False   ],
         'SIDESWIPER': [straight_key.action,        straight_key.action,        False   ]
         }

# set paddle type
#   returns True if setting succeeded
#
def settype(ptype):
    global paddle_type
    global tune_speed

    ptype=ptype.upper()
    if ptype in typetab.keys():
        inPort.bind(inPort.In_A, typetab[ptype][0])
        inPort.bind(inPort.In_B, typetab[ptype][1])
        paddle_type=ptype
        tune_speed=typetab[ptype][2]
        return True
    else:
        return False

# return paddle type
#
def gettype():
    return paddle_type

def initialize():
    global iambic_thread_handle
    iambic_thread_handle = threading.Thread(target=iambic_key_thread)
    iambic_thread_handle.start()

# terminate process
#
def terminate():
    global ev_terminate
    global iambic_thread_handle
    # terminate iambic subthread
    #
    ev_terminate=True
    ev_trigger.set()
    iambic_thread_handle.join()