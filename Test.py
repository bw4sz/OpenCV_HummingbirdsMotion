#########Simple Motion Sensing###############

#Testing read values and simple diff function

import cv2
import cv2.cv as cv
import numpy as np

#Set location of the file directory
fileD="C:/Users/Jorge/Documents/OpenCV_HummingbirdsMotion/"


#Set the file path to video

fP=fileD+"PlotwatcherTest.tlv"

#Begin with a still image test to show that package works.
photo = fileD+"17.jpg"

# Load an color image in grayscale
img = cv2.imread(photo)
cv2.imshow('my window',img)
cv2.waitKey(0)
cv2.destroyWindow('my window')

#Define Input Video file
videoPath=fileD+"PlotwatcherTest.tlv"
cap = cv2.VideoCapture(videoPath)
ret, frame = cap.read()

#show first image
cv2.imshow('frame',frame)
cv2.waitKey(10000)
cv2.destroyWindow('frame')

#Capture Information
nFrames = int(cap.get(cv.CV_CAP_PROP_FRAME_COUNT))
fps = cap.get(cv.CV_CAP_PROP_FPS)

print("Num. frames = ",nFrames)
print("Frame rate = ", fps, " fps")


# Play Video 
while(cap.isOpened()):
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('frame',frame)
    if cv2.waitKey(100) & 0xFF == ord('q'):
        cv2.destroyWindow('frame')
        break
cv2.destroyWindow('frame')


# TO DO: Mark a Mouse ROI selection


#cvSetImageROI()

# Difference between sample frames

def diffImg(t0, t1, t2):
  d1 = cv2.absdiff(t2, t1)
  d2 = cv2.absdiff(t1, t0)
  return cv2.bitwise_and(d1, d2)

#Need to reinitiate the video
cap = cv2.VideoCapture(videoPath)

#get a frame count
framecount = cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
print(framecount)
#start the iterator
frames=0
winName = "Movement Indicator"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)

#End the loop if there are no more frames

# Read three images first:
t_minus = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
t = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
t_plus = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)

#Create an empty array
diffsArray = []

#While there are frames left, subtract three since you all ready grabbed them from above.
while frames < framecount-3:
  diffs=diffImg(t_minus, t, t_plus)
#Add the difference to an output array
  diffsArray.append(diffs)
  cv2.imshow( winName,diffs)
  frames +=1
  #Place into the holder
    
  # Read next image
  t_minus = t
  t = t_plus
  t_plus = cv2.cvtColor(cap.read()[1], cv2.COLOR_RGB2GRAY)
  key = cv2.waitKey(500)
  if key == 27:
    cv2.destroyWindow(winName)
    break
cv2.destroyWindow(winName)

print "Goodbye"

cv2.destroyWindow(winName)