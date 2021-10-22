import pigpio
import RPi.GPIO as GPIO
import time

import logging
logger = logging.getLogger(__name__)

import threading, queue

class Servo():
    def __init__(self, pin, min_angle=-90, max_angle=90, min_pulse_width=500, max_pulse_width=2500):
        self.pin = pin
        self.min_angle=min_angle
        self.max_angle=max_angle
        self.min_pulse_width=min_pulse_width
        self.max_pulse_width=max_pulse_width

        self.pwm = pigpio.pi()
        self.pwm.set_mode(pin, pigpio.OUTPUT)
        
    # Specify a fractional distance instead of an absolute angle
    def set_fraction(self, fraction, minimum=-30, maximum=30):
        angle = (maximum - minimum) * fraction
        self.set_angle(angle)

    # Move Servo to desired angle
    def set_angle(self, angle):
        # Turn on PWM on servo pin
        self.pwm.set_PWM_frequency(self.pin, 50)
        
        # Cap the min/max angle
        if (angle > self.max_angle):
            angle = self.max_angle
        if (angle < self.min_angle):
            angle = self.min_angle

        # Work out the pulse width based on the angle
        pulsewidth = int(((angle / (self.max_angle - self.min_angle)) * (self.max_pulse_width - self.min_pulse_width)) + self.min_pulse_width)
        
        # TODO: change to logging package.
        print(f"angle = {angle}, max_angle-min_angle = {self.max_angle-self.min_angle}, pulse_range = {self.max_pulse_width-self.min_pulse_width}, pulsewidth = {pulsewidth}")
        
        # Set the pulse
        self.pwm.set_servo_pulsewidth(self.pin, pulsewidth)

        # Wait for servo to move
        # TODO: Change this to a fractional sleep based on the amount moved.
        time.sleep(0.5)

        # Turn servos off to reduce idle jitter
        self.pwm.set_PWM_dutycycle(self.pin,0)
        self.pwm.set_PWM_frequency(self.pin,0)


class ThreadingServo(Servo):
    q = queue.Queue()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.debug("Starting servo worker thread")
        threading.Thread(target=self.worker, daemon=True).start()

    def set_angle(self, angle):
        self.q.put(angle)

    def worker(self):
        while True:
            angle = self.q.get()
            self.set_angle(angle)
            self.q.task_done()