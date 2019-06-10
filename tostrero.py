import RPi.GPIO as GPIO
import time

from flask import Flask
from flask import request

app = Flask(__name__)


def setup_wheels(func):
    # @functools.wraps(func) but ngehh import
    # Huh. Even if it's local, can't have def wrapper(blah) both
    # here and in setup_eyes
    def wrapper_wheels(*args, **kwargs):
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
    return wrapper_wheels


def setup_eyes(func):
    # @functools.wraps(func) but ngehh import
    def wrapper_eyes(*args, **kwargs):
        # Something something
        GPIO.setmode(GPIO.BCM)
        signalpin = 12
        GPIO.setup(signalpin, GPIO.OUT, initial=GPIO.LOW)
        pwm_s = GPIO.PWM(signalpin, 50) # channel, hertz

        value = func(pwm_s, *args, **kwargs)

        GPIO.cleanup()

        return value
    return wrapper_eyes


@app.route('/')
def hello_world():
    return 'I am Tostrero. Please hit /go or something'


@app.route('/cleanup')
def cleanup():
    # For graceful exit in debugging ha
    try:
        GPIO.cleanup()
        return 'Cleaned up gpio'
    except:
        return 'Something went wrong with gpio cleanup'


@app.route('/go')
@setup_wheels
def go(ain1, ain2, pwm_a, bin1, bin2, pwm_b):
    """
    Errrrr I guess we decided that
    A=left wheel B=right wheel
    0 = stationary 1 = forward 2 = backwards
    and we'll mod 3 so that -1 is also backwards plus no errors
    Expecting following URL parameters: l, r, lspeed, rspeed, duration
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
        GPIO.output(ain1, GPIO.HIGH)
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

    ls = int(request.args.get('lspeed', 30)) % 100
    ls = 100 if request.args.get('lspeed', 0) == "100" else ls # haha
    rs = int(request.args.get('rspeed', 30)) % 100
    rs = 100 if request.args.get('rspeed', 0) == "100" else rs # haha
    pwm_a.start(ls)
    pwm_b.start(rs)

    d = int(request.args.get('duration', 3)) % 10 # idk, arbitrary limit
    d = 10 if request.args.get('duration', 0) == "10" else d # haha
    time.sleep(d)

    dir_dict = {0: 'никуда', 1: 'вперёд', 2: 'назад'}

    info = "Левое " + dir_dict[l%3] + ", скорость " + str(ls) + ". "\
        + "Правое " + dir_dict[r%3] + ", скорость " + str(rs) + ". "\
        + "Продолжительность " + str(d) + ". "

    return info


@app.route('/look')
@setup_eyes
def look(pwm_s):
    """
    Will take a float 0 to 10 and interpolate to the nice range.
    Not 0-9, but 0-10, because people find that more natural I guess.

    The safe range for duty cycle seems to be around 2.5 to around 12.0.
    The nice range for duty cycle should be like 6.5 to 9.0.
    The neutral position is dc 7.5.
    (But servo neutral doesn't translate to camera neutral so who cares...)
    """
    # These will probably change so I'll stick em all up here
    api_min = 0
    api_max = 10
    dc_min = 6.5
    dc_max = 9.0

    h = float(request.args.get('height'))
    h = max(h, api_min)
    h = min(h, api_max)
    dc = dc_min + (h/api_max)*(dc_max-dc_min)

    pwm_s.start(dc)
    time.sleep(1)
    pwm_s.stop()

    return "Высота " + str(h) + ", коэффициент заполнения " + str(dc) + ". "
