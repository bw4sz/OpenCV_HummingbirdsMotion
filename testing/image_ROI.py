import cv2
import numpy as np

drawing = False # true if mouse is pressed
ix,iy = -1,-1

roi=[]

cap = cv2.VideoCapture("C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/testing/PlotWatcherTest.tlv")
orig=cap.read()[1]

# mouse callback function
def draw_circle(event,x,y,flags,param):
    global ix,iy,drawing,mode

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            cv2.rectangle(orig,(ix,iy),(x,y),(0,255,0),-2)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        box=cv2.rectangle(orig,(ix,iy),(x,y),(0,255,0),-2)
        roi_pts=ix,iy,x,y
        roi.extend(roi_pts)
        k=27
             
cv2.namedWindow('image')
cv2.setMouseCallback('image',draw_circle)

while(1):
    cv2.imshow('image',orig)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

orig_ROI=orig.copy()
orig_ROI=orig_ROI[roi[1]:roi[3], roi[0]:roi[2]]

cv2.imshow('image',orig_ROI)
cv2.waitKey(10000)
cv2.destroyAllWindows()
