import pigpio
import RPi.GPIO as GPIO

import logging
logger = logging.getLogger(__name__)

import threading, queue

class Servo():
    def __init__(self, pin, min_angle=-90, max_angle=90, offset=0, min_pulse_width=500, max_pulse_width=2500, movement_delay=0.5):
        self.pin = pin
        self.min_angle=min_angle
        self.max_angle=max_angle
        self.min_pulse_width=min_pulse_width
        self.max_pulse_width=max_pulse_width
        self.movement_delay=movement_delay
        self.offset = offset

        # Use pigpio to handle the PWM on the GPIO pin
        self.pwm = pigpio.pi()
        self.pwm.set_mode(pin, pigpio.OUTPUT)
        logger.debug(f"New servo on GPIO pin {self.pin}")
        self.timerthread = None

        logging.debug("Starting servo worker thread")
        # Create a queue to communicate between threads, and start the queue listening thread
        self.q = queue.Queue()
        threading.Thread(target=self.worker, daemon=True, name=f"Servo-{self.pin}-Worker").start()

        
    # Specify a fractional distance instead of an absolute angle
    def set_fraction(self, fraction, minimum=-30, maximum=30):
        angle = minimum + ((maximum - minimum) * fraction)
        self.set_angle(angle)

    # From and input angle, calculate the pulse width to be sent to the servo
    def calculate_pulse_width(self, angle):
        angle_range = float(self.max_angle - self.min_angle)
        fractional = (angle + angle_range/2) / angle_range
        pulse_width = (fractional * (self.max_pulse_width - self.min_pulse_width)) + self.min_pulse_width
        return int(pulse_width)

    # Queue up an angle change for the servo
    def set_angle(self, angle):
        logger.debug(f"set_angle {angle} for servo {self.pin}")
        self.q.put(angle + self.offset)

    # Move Servo to desired angle
    def _set_angle(self, angle):
        # If we have a pending timer thread, cancel it.
        if self.timerthread:
            self.timerthread.cancel()

        # Turn on PWM on servo pin
        self.pwm.set_PWM_frequency(self.pin, 50)
        
        # Cap the min/max angle
        if (angle > self.max_angle):
            angle = self.max_angle
        if (angle < self.min_angle):
            angle = self.min_angle

        # Work out the pulse width based on the angle
        pulsewidth = self.calculate_pulse_width(angle)
        
        logger.debug(f"servo = {self.pin}, angle = {angle}, pulsewidth = {pulsewidth}")
        
        # Set the pulse
        self.pwm.set_servo_pulsewidth(self.pin, pulsewidth)

        # Create a timer thread to turn off the PWM on the pin to prevent jitter
        # PWM is software controlled on the pi, they'll make a lot of idle noise
        # if we don't do this.
        # The delay of 2 seconds is to allow the servo to move to the desired angle.
        self.timerthread = threading.Timer(2, self.turn_off_pwm)
        self.timerthread.start()
        self.timerthread.name = f"Servo-{self.pin}-StopTimer"

    # Turn off PWM for the GPIO pin the servo is connected to, to prevent jitter.
    def turn_off_pwm(self):
        logger.debug(f'Turning off PWM on pin {self.pin}')
        self.pwm.set_PWM_dutycycle(self.pin,0)
        self.pwm.set_PWM_frequency(self.pin,0)
        self.stop_event = None

    # Main thread loop to listen to incoming position requests via the queue.
    def worker(self):
        while True:
            logger.debug('Waiting for queued message')
            try:
                angle = self.q.get(block=True, timeout=10)
                logger.debug(f'Recieved {angle} from queue, setting it')
                self._set_angle(angle)
                logger.debug('Queued task done')
                self.q.task_done()
            except queue.Empty:
                logger.debug('Queue was empty, retrying.')