#Following Swinnen (2014) from:
###A Novel Method to Reduce Time Investment When Processing Videos from Camera Trap Studies###

#Import Libraries
import cv2 
import numpy as np
import argparse
import os
from shapely.ops import cascaded_union
import shapely.geometry as sg
import SwinnenSource


#Define command line arguments
parser = argparse.ArgumentParser()

#Video file
parser.add_argument("-f", help="path of single video",type=str,default="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv")
#threshold for variance
parser.add_argument("-t", help="threshold",type=int)

f="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv"
#f ='C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/ReviewDocuments/tinyshark.avi'
#f='C:\Users\Ben\Dropbox\Thesis\Automated_Monitering\sharkpass2.avi'
#f ='C:/Users/Ben/Desktop/MeerkatTest/Bird.mpg'

#read in video file
cap=cv2.VideoCapture(f)


#get info of file
#read in frame 
_,img=cap.read()

##Initiate two background subtractors
motion=SwinnenSource.MotionM(f,70,0.35)
static=SwinnenSource.Static(f,70)
mog=SwinnenSource.MOG(f,20,9)


cap=cv2.VideoCapture(f)

motion_holder=[]

##Capture next frame, if there is no next frame; break.
counter=0
while (1):
    counter=counter+1    
    print(counter)
    ret,i = cap.read()
    if not ret:
        break
    s=static.staticA(i.copy())
    m=motion.accAvg(img=i,towrite=s)
    #g=mog.run(img=i,towrite=s)
    motion_holder.append(m)
                         

##Output location
#file destination folder
dest="C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/ReviewDocuments/"

#make folder to hold output using the file name
flname=os.path.splitext(os.path.basename(f))[0]
outdr=os.path.join(dest,flname)   

#make folder
if not os.path.exists(outdr): os.mkdir(outdr)
    
vidname=os.path.join(dest,flname,"Comparison.avi")

height=np.size(motion_holder[0],1)
width=np.size(motion_holder[0],0)


codec=cv2.VideoWriter_fourcc('X','V','I','D')
out = cv2.VideoWriter(vidname,codec,30,(height,width),True)    

print(out.isOpened())

cv2.namedWindow("frame")
for i in  motion_holder: 
    cv2.imshow('frame',i)
    cv2.waitKey(20)
    
for i in  motion_holder: out.write(i)
            
out.release()
cv2.destroyAllWindows()        
