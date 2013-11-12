import cv2
#import cv2.cv as cv
import numpy as np

#Begin with a still image test to show that package works.
photo = 'C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/17.jpg'

# Load an color image in grayscale
#img = cv2.imread(photo)
#cv2.NamedWindow('my window', cv.CV_WINDOW_AUTOSIZE)
#cv2.imshow('my window',img)
#cv2.waitKey(0)
#cv2.destroyWindow('my window')

#Try a sample HD video
#Define Input file
#Sample file from online
cap = cv2.VideoCapture("C:/Users/Ben/Dropbox/Thesis/Maquipucuna_SantaLucia/openCV/MVI_0572.AVI")
ret, frame = cap.read()

print(frame)
#show first image
cv2.imshow('frame',frame)
cv2.waitKey(100)
cv2.destroyWindow('frame')

