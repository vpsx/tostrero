# 2019-03-31. Just spinning wheels -_-

print("There is life.")

import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

pin_ain1 = 13
pin_ain2 = 19
pin_apwm = 26

pin_bin1 = 16
pin_bin2 = 20
pin_bpwm = 21

# How to pick frequency? Basically you want it to be
# high enough that motor only sees the average.
# Makes sense. "Motor is low pass filter" ooookay
# But not too high, because of reasons.
# Also nice if you are outside audible range lol but ehh.
# Internets seem to suggest in the 2-20 KHz range...

gpio.setup(pin_ain1, gpio.OUT, initial=gpio.HIGH)
gpio.setup(pin_ain2, gpio.OUT, initial=gpio.LOW)
gpio.setup(pin_apwm, gpio.OUT, initial=gpio.HIGH)
pwm_a = gpio.PWM(pin_apwm, 2000)

gpio.setup(pin_bin1, gpio.OUT, initial=gpio.HIGH)
gpio.setup(pin_bin2, gpio.OUT, initial=gpio.LOW)
gpio.setup(pin_bpwm, gpio.OUT, initial=gpio.HIGH)
pwm_b = gpio.PWM(pin_bpwm, 2000)

pwm_a.start(50)
pwm_b.start(50)

time.sleep(20)

pwm_a.stop()
pwm_b.stop()

gpio.cleanup()
