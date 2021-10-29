import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera

import logging
import sys
import threading, queue
import time

import numpy as np

logger = logging.getLogger(__name__)


class MotionDetection:
    def __init__(self, camera_source=0, detection_callback=None, output_file=None):
        """Motion detection using opencv.

        Example usage:
        def detection_callback(x, w, size):
            logger.debug(f"Callback recieved: x = {x}, w = {w}, size = {size}")

        m = MotionDetection(detection_callback=detection_callback, output_file='output.avi')

        The detection_callback function will be called any time movement is detected, with 
        the x position in the frame, width, and the size of the frame.

        There is currently no vertical component of the motion passed to the callback function.
        """ 

        # Use OpenCV video capture, picamera is probably better here but couldn't make it work.
        logger.info('Opening Video Capture')
        self.cap = cv2.VideoCapture(camera_source)
        logger.debug('Wait for camera warmup')
        time.sleep(2)

        # Create the background subtraction filter for use when detecting 
        self.bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=False)
        self.kernel = np.ones((20,20), np.uint8)
        self.detection_callback = detection_callback if detection_callback else None
        self.output_file = output_file

        # Fire off the main detection thread
        threading.Thread(target=self.capture_loop, daemon=True, name="MotionDetection").start()

    def capture_loop(self):
        if self.output_file:
            self.writer = cv2.VideoWriter("output.avi", cv2.VideoWriter_fourcc(*"MJPG"), 10, (640,480))

        try:    
            logger.info('Starting capture loop')
            while True:
                logger.debug('Read image from capture stream')
                _, img = self.cap.read()

                # This should be an option.
                img = cv2.rotate(img, cv2.ROTATE_180)

                # Apply the background mask, do some funkyness (morphology, blur, threshold),
                # Find the contours and then calculate the areas of those contours.
                fgmask = self.bg.apply(img)
                fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, self.kernel)
                fgmask = cv2.medianBlur(fgmask, 5)
                _, fgmask = cv2.threshold(fgmask, 196, 255, cv2.THRESH_BINARY)
                contours, heirachy = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c)]

                image_width = img.shape[1]

                logger.debug(f'Found {len(areas)} movement areas')

                # If we've found some motion, it's saved as an area.
                if len(areas) >= 1:
                    # Find the largest object with motion in the frame, it's the one with the largest area
                    max_index = np.argmax(areas)
                    cnt = contours[max_index]
                    x, y, w, h = cv2.boundingRect(cnt)

                    # Add the bounding box to the output frame if we've set a filename
                    if self.output_file:
                        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

                    if self.detection_callback:
                        logger.debug(f'Calling callback with data (x={x}, w={w}, image_width={image_width})')
                        self.detection_callback(x,w,image_width)

                # Write frame to output file.
                if self.output_file:
                    self.writer.write(img)
        finally:
            logger.info('Closing Video Capture')
            self.cap.release()
            if self.output_file:
                self.writer.release()

# Standalone motiondetect test code.
if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG
    )

    def detection_callback(x, w, size):
        logger.debug(f"Callback recieved: x = {x}, w = {w}, size = {size}")

    m = MotionDetection(detection_callback=detection_callback, output_file='output.avi')

    while True:
        logger.debug("Main thread sleeping")
        time.sleep(60)