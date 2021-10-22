from servos import ThreadingServo
import motiondetect
import logging
import sys
import time

servos = [
  ThreadingServo(17, min_pulse_width=1/1000.0, max_pulse_width=2/1000.0),
  ThreadingServo(27),
  ThreadingServo(23)
]

Lid = servos[0]
LeftEye = servos[1]
RightEye = servos[2]

if __name__ == "__main__":
    # Log to stdout
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)

    logger.debug('Start motion detection')
    motiondetect.threading_capture_loop()

    while True:
        logger.debug('Move Servo')
        LeftEye.set_angle(-90)
        time.sleep(1)
        logger.debug('Move Servo Again')
        LeftEye.set_angle(0)
        time.sleep(1)