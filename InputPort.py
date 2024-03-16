# InputOutputPort_pigpio - interface to sense/control hardware port

# This module uses pigpio library.
#   http://abyz.me.uk/rpi/pigpio/
#
import pigpio

pi=pigpio.pi()
if not pi.connected:
    exit()

#   The numbers are Broadcom's GPIO number of BCM2835,
#   not RPi's assigned numbers.
In_A=23
In_B=24
In_C=25

def initialize_input_ports():
    for port in [In_A, In_B, In_C]:

        pi.set_mode(            port, pigpio.INPUT)
        pi.set_pull_up_down(    port, pigpio.PUD_UP)

        # debounce; tolerance is 3ms.
        pi.set_glitch_filter(port, 3000)


# check current port status
#
def check_port(port):
    import KeyingControl as key

    if pi.read(port)==0:
        return key.PRESSED
    else:
        return key.RELEASED

# table for callback functions by every input port
#   empty at initial state
#
cb={}

# bind callback function to input port
#   This function is interface between pigpio and our
#   abstraction layer.
#
#   func is a function which has only parameter: func(state)
#
def bind(in_port, func):
    import KeyingControl as key

    if in_port in cb:
        cb[in_port].cancel()  #  unassign current callback if any

    cb[in_port]=pi.callback(in_port,
                            pigpio.EITHER_EDGE,
                            lambda p, s, t: func(key.PRESSED
                                                 if s==0
                                                 else key.RELEASED))

# termination process for this module
#
def terminate():
    # unbound all callbacks
    #
    for in_port in cb.keys():
        if in_port in cb:
            cb[in_port].cancel()

    # close connection to pigpiod
    #
    pi.stop()