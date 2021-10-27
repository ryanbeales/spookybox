from servos import Servo
from motiondetect import MotionDetection
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

    Lid = Servo(17, min_pulse_width=1/1000.0, max_pulse_width=2/1000.0),
    LeftEye = Servo(27)
    RightEye = Servo(23, offset=-10)

    def detection_callback(x, w, size):
        logger.debug(f"Motion Detected: x = {x}, w = {w}, size = {size}")

        # If detected movement is less than 10% of the frame, ignore it.
        if (w/size) < 0.1:
            logger.debug('Movement detected is not large enough, ignoring')
            return

        fractional = (x + w/2) / size
        LeftEye.set_fraction(1-fractional)
        RightEye.set_fraction(1-fractional)

    logger.debug('Start motion detection')
    m = MotionDetection(detection_callback=detection_callback, output_file='output.avi')

    while True:
        logger.debug('sleeping main thread')
        time.sleep(60)