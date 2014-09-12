import numpy as np
import cv2

cap = cv2.VideoCapture('C:/Users/Ben/Downloads/exampleMB.mp4')

fgbgMOG2 = cv2.createBackgroundSubtractorMOG2()
fgbgKNN = cv2.createBackgroundSubtractorMOG2()

while(1):
    ret, frame = cap.read()

    fgmask = fgbgMOG2.apply(frame)
    fgmaskKNN = fgbgKNN.apply(frame)

    cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    cv2.imshow('frame',fgmask)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    
    cv2.namedWindow('frameKNN', cv2.WINDOW_NORMAL)    
    cv2.imshow('frameKNN',fgmaskKNN)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break
    

cap.release()
cv2.destroyAllWindows()