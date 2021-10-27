import pigpio
import RPi.GPIO as GPIO

import logging
logger = logging.getLogger(__name__)

import threading, queue

# Add logging to this one.
class Servo():
    def __init__(self, pin, min_angle=-90, max_angle=90, offset=0, min_pulse_width=500, max_pulse_width=2500, movement_delay=0.5):
        self.pin = pin
        self.min_angle=min_angle
        self.max_angle=max_angle
        self.min_pulse_width=min_pulse_width
        self.max_pulse_width=max_pulse_width
        self.movement_delay=movement_delay
        self.offset = offset

        self.pwm = pigpio.pi()
        self.pwm.set_mode(pin, pigpio.OUTPUT)
        logger.debug(f"New servo on GPIO pin {self.pin}")
        self.timerthread = None

        logging.debug("Starting servo worker thread")
        self.q = queue.Queue()
        threading.Thread(target=self.worker, daemon=True, name=f"Servo-{self.pin}-Worker").start()

        
    # Specify a fractional distance instead of an absolute angle
    def set_fraction(self, fraction, minimum=-30, maximum=30):
        angle = (maximum - minimum) * fraction
        self.set_angle(angle)

    def calculate_pulse_width(self, angle):
        angle_range = float(self.max_angle - self.min_angle)
        fractional = (angle + angle_range/2) / angle_range
        pulse_width = (fractional * (2500 - 500)) + 500
        return int(pulse_width)


    def set_angle(self, angle):
        logger.debug(f"set_angle {angle} for servo {self.pin}")
        self.q.put(angle + self.offset)

    # Move Servo to desired angle
    def _set_angle(self, angle):
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
        self.timerthread = threading.Timer(2, self.turn_off_pwm)
        self.timerthread.start()
        self.timerthread.name = f"Servo-{self.pin}-StopTimer"

    def turn_off_pwm(self):
        logger.debug(f'Turning off PWM on pin {self.pin}')
        self.pwm.set_PWM_dutycycle(self.pin,0)
        self.pwm.set_PWM_frequency(self.pin,0)
        self.stop_event = None

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