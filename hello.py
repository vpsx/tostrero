# 2019-03-31. Here we go!
# First ever Raspberry Pi script.
# Make LED do some stuff; make code run; do PWM things.
# Keep as cheatsheet...

print("There is life.")

try:
    import RPi.GPIO as gpio
    print("Successfully imported RPi.GPIO")
except RuntimeError:
    print("Error importing RPi.GPIO... Probably need to run script with sudo.")

import time
print("Imported time too.")

mypin = 12
print("mypin = " + str(mypin))

print("Mode = " + str(gpio.getmode()))
gpio.setmode(gpio.BCM) # Broadcom, I guess. Alternative is BOARD
print("Mode = " + str(gpio.getmode()))

#print(gpio.RPI_INFO)
#print(gpio.RPI_INFO['P1_REVISION'])
#print(gpio.VERSION)

# Channel is the number based on BCM.
# gpio.setup(mypin, gpio.IN)
gpio.setup(mypin, gpio.OUT, initial=gpio.LOW)

# myinputval = gpio.input(channel)

# A thing. time.sleep(seconds)
print("On-off 5 cycles")
for i in range(5):
    print(i)
    gpio.output(mypin, gpio.HIGH)
    time.sleep(0.5)
    gpio.output(mypin, gpio.LOW)
    time.sleep(0.5)
print("Done cycling")

# To blink an LED once every 2s using PWM(!)
print("Blink every 2s until you hit enter")
p = gpio.PWM(mypin, 0.5) # That's channel, frequency in Hz
p.start(1) # That's the duty cycle (0.0 <= dc <= 100.0)
raw_input("Press return to stop the LED:") # Just input for Py3
p.stop()

# To brighten and dim
p.ChangeFrequency(50)
p.start(0)
print("Starting the brighten and dim loop. KeyboardInterrupt to stop.")
try:
    while 1:
        for dc in range(0, 101, 5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.1)
        for dc in range(100, -1, -5):
            p.ChangeDutyCycle(dc)
            time.sleep(0.1)
except KeyboardInterrupt:
    print("KeyboardInterrupt. Stopping")

p.stop()

gpio.cleanup()
