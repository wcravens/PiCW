# InputOutputPort_pigpio - interface to sense/control hardware port

# This module uses pigpio library.
#   http://abyz.me.uk/rpi/pigpio/
#
import pigpio

pi=pigpio.pi()
if not pi.connected:
    exit()

Out_T=22  # TX Control line
Out_M=18  # PWM output - for side tone

def initialize_output_ports():
    pi.set_mode(Out_M, pigpio.OUTPUT)
    # ( gpio, PWMfreq, PWMduty )
    pi.hardware_PWM(Out_M, 0, 0)

# activate TX control line
#
def txline_on():
    pi.write(Out_T, 1)

# deactivate TX control line
#
def txline_off():
    pi.write(Out_T, 0)

# activate side tone
#
def beep_on():
    pi.set_PWM_dutycycle(Out_M, 128)

# deactivate side tone
#
def beep_off():
    pi.set_PWM_dutycycle(Out_M, 0)

# get side tone frequency
#
def get_beepfreq():
    return pi.get_PWM_frequency(Out_M)

# set side tone frequency
#
def set_beepfreq(hz):
    pi.set_PWM_frequency(Out_M, hz)


# get available side tone frequencies
#
def get_avail_beepfreq():
    saved_freq=get_beepfreq()

    set_beepfreq(50000)    # try too high freq
    hi_freq=get_beepfreq() # get actual result

    set_beepfreq(saved_freq)  # restore saved setting

    return [int(hi_freq/div_ratio+0.5)
            for div_ratio in [1, 2, 4, 5, 8,
                              10, 16, 20, 25, 32, 40, 50, 80,
                              100, 160, 200, 400, 800]]

def terminate():

    txline_off()
    beep_off()
    pi.stop()