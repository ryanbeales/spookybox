import cv2

import logging
import threading, queue
import time

import numpy as np

logger = logging.getLogger(__name__)

def capture_loop():
    logger.info('Opening Video Capture')
    cap = cv2.VideoCapture(0)
    bg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=False)
    kernel = np.ones((20,20), np.uint8)

    try:    
        logger.info('Starting capture loop')
        while True:
          logger.debug('Read image from capture stream')
          _, img = cap.read()
          
          fgmask = bg.apply(img)
          fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)
          fgmask = cv2.medianBlur(fgmask, 5)
          _, fgmask = cv2.threshold(fgmask, 196, 255, cv2.THRESH_BINARY)
          contours, heirachy = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
          areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 20000]
 
          image_width = img.shape[1]

          logger.debug(f'Found {len(areas)} movement areas')

          if len(areas) >= 1:
              max_index = np.argmax(areas)
              cnt = contours[max_index]
              x, y, w, h = cv2.boundingRect(cnt)
              logger.debug(f"Center of largest movement{x + (w/2)} of size {image_width}")

    finally:
        logger.info('Closing Video Capture')
        cap.release()

def threading_capture_loop():
    threading.Thread(target=capture_loop, daemon=True, name="MotionDetection").start()

if __name__ == '__main__':
    capture_loop()