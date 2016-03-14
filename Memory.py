import cv2 
import glob
import os
import cv2.bgsegm


#File formats
ext="C:/Users/Ben/Desktop/pics2/*.jpg"

#Create mog
b=cv2.createBackgroundSubtractorMOG2(setUseOpenCL=False)

#Find photos
jpgs=[]
jpgs.extend(glob.glob(ext))

#Read in photos and add to background
for x in jpgs:
    current_image=cv2.imread(x)
    print("Photo size is %s" % str(current_image.shape))
    cv2.imshow("image",current_image)
    cv2.waitKey(10)
    b.apply(current_image,setUseOpenCL=False)
    del(current_image)
    
