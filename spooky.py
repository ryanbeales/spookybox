from servos import Servo
import motiondetect
import logging
import sys
import time

if __name__ == "__main__":
    # Log to stdout
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    logger.debug('Start motion detection')
    motiondetect.threading_capture_loop()

    Lid = Servo(17, min_pulse_width=1/1000.0, max_pulse_width=2/1000.0),
    LeftEye = Servo(27)
    RightEye = Servo(23)

    while True:
        logger.debug('Move Servo')
        LeftEye.set_fraction(0)
        RightEye.set_fraction(0)
        time.sleep(5)
        LeftEye.set_fraction(1)
        RightEye.set_fraction(1)
        time.sleep(5)