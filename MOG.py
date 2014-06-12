import numpy as np
import cv2

cap = cv2.VideoCapture('C:/Users/Jorge/Documents/OpenCV_HummingbirdsMotion/testing/PlotwatcherTest.tlv')

fgbg = cv2.BackgroundSubtractorMOG(500,.6,.9,.1)

while(1):
    ret, frame = cap.read()

    fgmask = fgbg.apply(frame)

    cv2.imshow('frame',fgmask)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()