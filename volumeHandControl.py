import numpy as np
import cv2
import time
import handtrakingmodule as htm

wCam, hCam = 640, 480


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7)

while True:
        success, img = cap.read()
        
        img = detector.findHands(img)
        lmList = detector.handPosition(img, draw=False)
        
        cTime = time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        cv2.putText(img, f'FPS: {int(fps)}', (40, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        
        cv2.imshow('Image', img)
        cv2.waitKey(1)