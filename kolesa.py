import RPi.GPIO as GPIO
import time

from flask import Flask
from flask import request

app = Flask(__name__)


def setup_wheels(func):
    # @functools.wraps(func) but ngehh import
    def wrapper(*args, **kwargs):
        GPIO.setmode(GPIO.BCM)

        pin_ain1 = 13
        pin_ain2 = 19
        pin_apwm = 26

        pin_bin1 = 16
        pin_bin2 = 20
        pin_bpwm = 21

        GPIO.setup(pin_ain1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_ain2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_apwm, GPIO.OUT, initial=GPIO.HIGH)
        pwm_a = GPIO.PWM(pin_apwm, 2000)

        GPIO.setup(pin_bin1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_bin2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(pin_bpwm, GPIO.OUT, initial=GPIO.HIGH)
        pwm_b = GPIO.PWM(pin_bpwm, 2000)

        # All that will not be in scope T^T
        value = func(
            pin_ain1,
            pin_ain2,
            pwm_a,
            pin_bin1,
            pin_bin2,
            pwm_b,
            *args,
            **kwargs
        )

        GPIO.cleanup()

        return value
    return wrapper


@app.route('/')
def hello_world():
    return 'I am Koleca. Please hit /go or something'


@app.route('/cleanup')
def cleanup():
    # For graceful exit in debugging ha
    GPIO.cleanup()
    return 'Cleaned up'


@app.route('/go')
@setup_wheels
def go(ain1, ain2, pwm_a, bin1, bin2, pwm_b):
    """
    Errrrr I guess we decided that
    A=left wheel B=right wheel
    0 = stationary 1 = forward 2 = backwards
    and we'll mod 3 so that -1 is also backwards plus no errors
    Expecting following URL parameters: l, r, speed, duration
    """
    l = int(request.args.get('l', 1))
    r = int(request.args.get('r', 1))

    # IDK, I suppose I should use elifs for early termination,
    # but I kinda like this...
    if l % 3 == 0:
        # Left wheel not moving
        GPIO.output(ain1, GPIO.LOW)
        GPIO.output(ain2, GPIO.LOW)
    if r % 3 == 0:
        # Right wheel not moving
        GPIO.output(bin1, GPIO.LOW)
        GPIO.output(bin2, GPIO.LOW)
    if l % 3 == 1:
        # Left wheel forward
        GPIO.output(ain1, GPIO.HIGH) # TODO just flip as necessary if turns out wrong haha
        GPIO.output(ain2, GPIO.LOW)
    if r % 3 == 1:
        # Right wheel forward
        GPIO.output(bin1, GPIO.HIGH)
        GPIO.output(bin2, GPIO.LOW)
    if l % 3 == 2:
        # Left wheel back
        GPIO.output(ain1, GPIO.LOW)
        GPIO.output(ain2, GPIO.HIGH)
    if r % 3 == 2:
        # Right wheel back
        GPIO.output(bin1, GPIO.LOW)
        GPIO.output(bin2, GPIO.HIGH)

    s = int(request.args.get('speed', 30)) % 100
    s = 100 if request.args.get('speed', 0) == "100" else s # haha
    pwm_a.start(s)
    pwm_b.start(s)

    d = int(request.args.get('duration', 3)) % 10 # idk, arbitrary limit
    d = 10 if request.args.get('duration', 0) == "10" else d # haha
    time.sleep(d)

    dir_dict = {0: 'никуда', 1: 'вперёд', 2: 'назад'}

    info = "Левое " + dir_dict[l%3] + ", правое " + dir_dict[r%3]\
        + ", скорость " + str(s) + ", продолжительность " + str(d)

    return info
