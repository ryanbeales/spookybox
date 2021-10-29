from servos import Servo
from motiondetect import MotionDetection
import logging
import sys
import time
import threading

# Create a Lid servo that will open/close the box.
class LidServo(Servo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.closetimer = None

    # Open the lid, and create a timer to close the lid.
    def open(self):
        if self.closetimer:
            self.closetimer.cancel()
        
        self.set_angle(-60)

        self.closetimer = threading.Timer(2, self.close)
        self.closetimer.start()

    def close(self):
        self.set_angle(20)


if __name__ == "__main__":
    # Log to stdout
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    # Create our servo objects
    Lid = LidServo(17)
    LeftEye = Servo(23, offset=-10) # Offset our Left eye slightly so it's looking in the right direction.
    RightEye = Servo(27)

    # Callback function for movement detection
    def detection_callback(x, w, size):
        logger.debug(f"Motion Detected: x = {x}, w = {w}, size = {size}")

        # If detected movement is less than 20% of the frame, ignore it.
        if (w/size) < 0.2:
            logger.debug('Movement detected is not large enough, ignoring')
            return

        # Open the lid
        Lid.open()
        # Work out where in the frame the movement was
        fractional = (x + w/2) / size
        # Set both eyes to look at the location of the movement
        LeftEye.set_fraction(1-fractional)
        RightEye.set_fraction(1-fractional)

    logger.debug('Start motion detection')
    m = MotionDetection(detection_callback=detection_callback)

    # Idle our main thread. Need to do something better here.
    while True:
        logger.debug('sleeping main thread')
        time.sleep(60)