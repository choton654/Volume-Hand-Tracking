import numpy as np
import cv2
import time
import handtrakingmodule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


wCam, hCam = 640, 480


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
# print(volume.GetVolumeRange())
volRang = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(-20.0, None)

minVol = volRang[0]
maxVol = volRang[1]

vol = 0
volBar = 400
volParc = 0
area = 0
while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList, bbox = detector.handPosition(img, draw=True)

    if len(lmList) != 0:
        # print(lmList[4], lmList[8])
        
        
        # filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        # print(area)

        if 250 < area < 1000:
            # print('yes',area)
            
            # Find distance between index and thumb
            length, img, lineInfo = detector.findDistance(4,8,img)
            # print(length)

            # Convert volume
            # vol = np.interp(length, [50, 300], [minVol, maxVol])
            volBar = np.interp(length, [50, 280], [400, 150])
            volParc = np.interp(length, [50, 280], [0, 100])
            # volume.SetMasterVolumeLevel(vol, None)
            # set smoothness
            smoothness = 10
            volParc = smoothness * round(volParc/smoothness)
            # check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volParc/100,None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)
            # hand range 50 - 300
            # volume range -65 - 0

            # print(int(length), vol)

            # if length < 50:
            #     cv2.circle(img, (lineInfo[4], lineInfo[5]), 10, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400),
                        (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volParc)} %', (40, 450),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Vol set: {int(cVol)} %', (400, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow('Image', img)
    cv2.waitKey(1)
