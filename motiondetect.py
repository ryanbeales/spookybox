import cv2

import logging
import threading, queue
import time

logger = logging.getLogger(__name__)

def capture_loop():
    logger.info('Opening Video Capture')
    cap = cv2.VideoCapture(0)

    classifer_name = 'haarcascade_upperbody.xml'
    logger.info('Loading cascade classifer: {classifer_name}')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + classifer_name)


    try:    
        logger.info('Starting capture loop')
        while True:
          logger.debug('Read image from capture stream')
          _, img = cap.read()
          logger.debug('Convert to grayscale')
          gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
          
          logger.debug('Detecting objects...')
          objects = face_cascade.detectMultiScale(gray,
                  scaleFactor=1.1,
                  minNeighbors=5,
                  minSize=(30,30),
                  flags=cv2.CASCADE_SCALE_IMAGE)

          image_width = img.shape[1]

          logger.debug(f'Found {len(objects)} objects')
          for o in objects:
             # If something is found, it's a set of (x,y,w,h)
             x = o[0]
             logger.debug(f"Found an object: x = {x}, image_width = {image_width}")
            
    finally:
        logger.info('Closing Video Capture')
        cap.release()

def threading_capture_loop():
    threading.Thread(target=capture_loop, daemon=True, name="MotionDetection").start()

if __name__ == '__main__':
    capture_loop()