# 2019-05-03.
print("Can servo motor?")

import time
try:
    import RPi.GPIO as gpio
    print("Successfully imported RPi.GPIO")
except RuntimeError:
    print("Error importing RPi.GPIO... Probably need to run script with sudo.")

mypin = 12
#mypin = 18
print("Stick signal wire on pin " + str(mypin))

gpio.setmode(gpio.BCM) # Broadcom, I guess. Alternative is BOARD

# Channel is the number based on BCM.
gpio.setup(mypin, gpio.OUT, initial=gpio.LOW)

p = gpio.PWM(mypin, 50) # That's channel, frequency in Hz
p.ChangeFrequency(50) # Useless code for the record

# Ah oh for servo motors you need milliseconds not duty cycle.
# The SG92R is 50Hz... and 1.0ms/1.5ms/2.0ms.
# 50Hz means it expects a pulse every 1000/50=20ms.
# According to Wikipedia the exact frequency doesn't matter?
# I have no idea how that works...
# Anyway so you want 1/20=5 to 2/20=10 duty cycle.

# It is very steady at 12% but not at lower pulse widths.
# That's pretty fascinating. I guess it makes sense?
# What if I lengthen the pulses, so lower the freq?
# ...Okay that screwed everything up ha.
# TODO:
# Need to not hardcode the duty cycles and fiddle with freq.

# TODO: Explore further. Clean up.
# TODO: Go investigate this jitter thing... is it normal
# It's a common problem. Servo buzz/noise/jitter/etc.

# These names don't make sense pepega
pausetime = 3
sleeptime = 0.1
dutystep = 0.5
dutymin = 3.0     #5.0; min is 2.5 before it's scary
dutymax = 12.0    #10.0; max is 12.0 before it's scary
dutymid = 7.5     #That should stay # (dutymin + dutymax)/2

dc = dutymin
p.start(dc)       #That's the duty cycle (0.0 <= dc <= 100.0)


print("Experiment One")
try:
    while 1:
        for pos in [dutymin, dutymid, dutymax, dutymid]:
            print(pos)
            p.ChangeDutyCycle(pos)
            time.sleep(pausetime)
except KeyboardInterrupt:
    print("Stopping experiment one")
    

print("Experiment Two")
try:
    while 1:
        while(dc < dutymax):
            print(dc)
            p.ChangeDutyCycle(dc)
            dc += dutystep
            time.sleep(sleeptime)
        while(dc > dutymin):
            print(dc)
            p.ChangeDutyCycle(dc)
            dc -= dutystep
            time.sleep(sleeptime)
except KeyboardInterrupt:
    print("KeyboardInterrupt. Stopping experiment two")


# Cleanup
p.stop()
gpio.cleanup()
