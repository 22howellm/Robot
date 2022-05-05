#https://www.hackster.io/ruchir1674/video-streaming-on-flask-server-using-rpi-ef3d75-----------------------#

import time
import io
import threading
import picamera
import picamera.array
import cv2
import numpy
import logging

class CameraInterface(object):

    def __init__(self, logger=logging.getLogger(), resolution = (320,240), framerate=32):
        self.frame = None  # current frame is stored here by background thread
        self.logger=logger
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.hflip = True; self.camera.vflip = True #not sure what this does
        self.rawCapture = io.BytesIO()
        self.stream = None
        self.thread = None
        self.stopped = False
        return

    def start(self):
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        self.log("CAMERA INTERFACE: Started Camera Thread")
        return
        
    def log(self, message):
        self.logger.info(message)
        return

    def get_frame(self):
        return self.frame

    def stop(self):
        self.stopped = True
        return

    # Thread reads frames from the stream
    def update(self):
        self.camera.start_preview()
        time.sleep(2)
        self.stream = self.camera.capture_continuous(self.rawCapture, 'jpeg', use_video_port=True)
        for f in self.stream:
            self.rawCapture.seek(0)
            self.frame = self.rawCapture.read()
            self.rawCapture.truncate(0)
            self.rawCapture.seek(0)

            # stop the thread
            if self.stopped:
                self.camera.stop_preview()
                time.sleep(2)
                self.rawCapture.close()
                self.stream.close()
                self.camera.close()
                self.log("CAMERA INTERFACE: Exiting Camera Thread")
                return
        return
    
    #detect if there is a colour in the image
    def get_camera_colour(self):
        if not self.frame: #hasnt read a frame from camera
            return "camera is not running yet"
        img = cv2.imdecode(numpy.fromstring(self.frame, dtype=numpy.uint8), 1)
        # set red range
        redlowcolor = (50,50,150)
        redhighcolor = (128,128,255)

        green_low_color = (0,255,0)
        green_high_color = (0,255,100)

        yellow_low_color = (0,200,255)
        yellow_high_color = (0,255,255)

        # threshold
        redthresh = cv2.inRange(img, redlowcolor, redhighcolor)
        greenthresh = cv2.inRange(img, green_low_color, green_high_color)
        yellowthresh = cv2.inRange(img, yellow_low_color, yellow_high_color)

        cv2.imwrite("threshold.jpg", redthresh)

        red_count = numpy.sum(numpy.nonzero(redthresh))
        green_count = numpy.sum(numpy.nonzero(greenthresh))
        yellow_count = numpy.sum(numpy.nonzero(yellowthresh))

        self.log("RED PIXELS: " + str(red_count))
        colour = None
        count = 0
        if green_count > yellow_count:
            colour = 'green'
            count = green_count
        else:
            colour = 'yellow'
            count = yellow_count
        print('amount of pixels: ' + str(count))
        if count > 300: #more than 300 pixels are between the low and high color
            print(str(colour))
            return str(colour)
        return "no colour"
if __name__ == '__main__':
    camera = CameraInterface()
    while True:
        camera.get_camera_colour()