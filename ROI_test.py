import cv2
import numpy

#read in file
orig=cv2.imread("C:\Users\Ben\Desktop\Oct.14\Oct.14\IMG_1838.jpg")
orig_ROI=orig.copy()

drawing=False
ix=0
iy=0
roi=[]

def Urect(img,title):

    def onmouse(event,x,y,flags,param):
        global ix,iy,roi,drawing

        # Draw Rectangle
        if event == cv2.EVENT_RBUTTONDOWN:
            drawing = True
            ix,iy = x,y

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                cv2.rectangle(img,(ix,iy),(x,y),(0,255,255),-1)
                rect = (ix,iy,abs(ix-x),abs(iy-y))

        elif event == cv2.EVENT_RBUTTONUP:
            drawing = False
            cv2.rectangle(img,(ix,iy),(x,y),(0,255,255),-1)
            rect = (ix,iy,x,y)
            roi.extend(rect)

    cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(title,onmouse)

    print ("Please draw a single rectangle ROI using right click!")
    while(1):
            cv2.namedWindow(title,cv2.WINDOW_AUTOSIZE)                 
            cv2.imshow(title,img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                    break
    
    cv2.destroyAllWindows()
    
    return(roi)    


roi_selected=Urect(orig,"Region of Interest")        

ROI_include="include"

#Include the portion 
if ROI_include == "include":
    display_image=orig_ROI[roi_selected[1]:roi_selected[3], roi_selected[0]:roi_selected[2]]

#Exclude the portion
if ROI_include == "exclude":
    orig_ROI[roi_selected[1]:roi_selected[3], roi_selected[0]:roi_selected[2]]=255
    display_image=orig_ROI

cv2.namedWindow("result",cv2.WINDOW_NORMAL)
cv2.imshow("result", display_image)
cv2.waitKey(0)