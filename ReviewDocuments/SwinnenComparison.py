#Following Swinnen (2014) from:
###A Novel Method to Reduce Time Investment When Processing Videos from Camera Trap Studies###

#Import Libraries
import cv2 
import numpy as np
import argparse
import os

#Define command line arguments
parser = argparse.ArgumentParser()

#Video file
parser.add_argument("-f", help="path of single video",type=str,default="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv")
#threshold for variance
parser.add_argument("-t", help="threshold",type=int)

#f="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv"
f ='C:/Users/Ben/Desktop/MeerkatTest/smallshark.avi'
#read in video file
cap=cv2.VideoCapture(f)

#file destination folder
dest="C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/ReviewDocuments/"

#make folder to hold output using the file name
flname=os.path.splitext(os.path.basename(f))[0]
outdr=os.path.join(dest,flname)

#make folder
if not os.path.exists(outdr): os.mkdir(outdr)

#get info of file
#read in frame 
_,img=cap.read()
width = np.size(img, 1)
height = np.size(img, 0)

#Step 1 - resize all frames
#Swinnen does not provide an explicit resize statement for different image types, so we will leave the default which is to cut in half.

#create empty frame to hold objects
mat=[]
frame_counter=0

while (1):
    #Capture next frame, if there is no next frame; break.
    ret,img = cap.read()
    frame_counter=frame_counter+1
    if not ret:
        break
    
    #resize and grayscale
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        
    res=cv2.resize(frame,(width/2,height/2))
    mat.append(res)

#new size
widthr=np.size(mat[0],0)
heightr=np.size(mat[0],1)


#set accumulator
background = np.float32(mat[0]) # 32 bit accumulator

for i in mat:
    cv2.accumulate(i,background)
    
#divide by number of frames
background=background/len(mat)

#write background image to file
#get filename of input
cv2.imwrite(os.path.join(dest,flname,"Background.jpg"), background)

#loop through all frames and compare to background to get residuals

#read in video file
cap=cv2.VideoCapture(f)

#empty frame to hold the difference between frame and background
diff_holder=[]

#compare the mean to each resized frame.
for i in mat:
    
    #current frame to average
    back_depth=cv2.convertScaleAbs(background)
    diff=cv2.absdiff(i,back_depth)
    
    #collect the difference frames
    diff_holder.append(diff)
    
#write video of frames to view.
codec=cv2.VideoWriter_fourcc('M','P','G','4')

out = cv2.VideoWriter(os.path.join(dest,flname,"Difference.avi"),-1,20,(np.size(diff_holder[0],0),np.size(diff_holder[0])))                    

for i in diff_holder:
        # write the  frame
        out.write(i)
        
# Release everything if job is finished
out.release()

print("done")

##split and sort the jpg names                
##Loop through every frame and write video

#cv2.namedWindow('diff', cv2.WINDOW_NORMAL)

#for i in diff_holder:
    #cv2.imshow("diff",i)
    #k = cv2.waitKey(100) & 0xff    
    #if k == 27:
        #break


    

    
