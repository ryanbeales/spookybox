import cv2

import logging
import sys
import threading, queue
import time

import numpy as np

logger = logging.getLogger(__name__)


class MotionDetection:
    def __init__(self, camera_source=0, detection_callback=None):
        logger.info('Opening Video Capture')
        self.cap = cv2.VideoCapture(camera_source)
        self.bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=False)
        self.kernel = np.ones((20,20), np.uint8)
        self.callback = detection_callback if detection_callback else None

        threading.Thread(target=self.capture_loop, daemon=True, name="MotionDetection").start()

    def capture_loop(self):
        try:    
            logger.info('Starting capture loop')
            while True:
                logger.debug('Read image from capture stream')
                _, img = self.cap.read()

                fgmask = self.bg.apply(img)
                fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, self.kernel)
                fgmask = cv2.medianBlur(fgmask, 5)
                _, fgmask = cv2.threshold(fgmask, 196, 255, cv2.THRESH_BINARY)
                contours, heirachy = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 20000]

                image_width = img.shape[1]

                logger.debug(f'Found {len(areas)} movement areas')

                if len(areas) >= 1:
                    max_index = np.argmax(areas)
                    cnt = contours[max_index]
                    x, y, w, h = cv2.boundingRect(cnt)

                    if self.callback:
                        logger.debug(f'Calling callback with data (x={x}, w={w}, image_width={image_width})')
                        self.callback(x,w,image_width)

        finally:
            logger.info('Closing Video Capture')
            self.cap.release()

if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG
    )

    def detection_callback(x, w, size):
        logger.debug(f"Callback recieved: x = {x}, w = {w}, size = {size}")

    m = MotionDetection(detection_callback=detection_callback)

    while True:
        logger.debug("Main thread sleeping")
        time.sleep(60)