import pigpio
import RPi.GPIO as GPIO
import time

import cv2

class Servo():
    def __init__(self, pin, min_angle=-90, max_angle=90, min_pulse_width=500, max_pulse_width=2500):
        self.pin = pin
        self.min_angle=min_angle
        self.max_angle=max_angle
        self.min_pulse_width=min_pulse_width
        self.max_pulse_width=max_pulse_width

        self.pwm = pigpio.pi()
        self.pwm.set_mode(pin, pigpio.OUTPUT)
        
    def set_fraction(self, fraction, minimum=-30, maximum=30):
        angle = (maximum - minimum) * fraction
        self.set_angle(angle)

    def set_angle(self, angle):
        self.pwm.set_PWM_frequency(self.pin, 50)
        
        if (angle > self.max_angle):
            angle = self.max_angle
        if (angle < self.min_angle):
            angle = self.min_angle

        pulsewidth = int(((angle / (self.max_angle - self.min_angle)) * (self.max_pulse_width - self.min_pulse_width)) + self.min_pulse_width)
        print(f"angle = {angle}, max_angle-min_angle = {self.max_angle-self.min_angle}, pulse_range = {self.max_pulse_width-self.min_pulse_width}, pulsewidth = {pulsewidth}")
        self.pwm.set_servo_pulsewidth(self.pin, pulsewidth)
        time.sleep(1)
        self.pwm.set_PWM_dutycycle(self.pin,0)
        self.pwm.set_PWM_frequency(self.pin, 0)
    


servos = [
  Servo(17, min_pulse_width=1/1000.0, max_pulse_width=2/1000.0),
  Servo(27),
  Servo(23)
]

Lid = servos[0]
LeftEye = servos[1]
RightEye = servos[2]

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

    try:    
        while True:
          _, img = cap.read()
          gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
          latest_image = gray
          print('Detecting...')
          objects = face_cascade.detectMultiScale(gray,
                  scaleFactor=1.1,
                  minNeighbors=5,
                  minSize=(30,30),
                  flags=cv2.CASCADE_SCALE_IMAGE)

          image_width = img.shape[1]

          for o in objects:
             # If something is found, it's a set of (x,y,w,h)
             x = o[0]
             print(f"Found an object: x = {x}, image_width = {image_width}")
             LeftEye.set_fraction(x/image_width)
             
    finally:
        cap.release()
