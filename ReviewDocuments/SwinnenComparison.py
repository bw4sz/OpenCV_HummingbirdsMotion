#Following Swinnen (2014) from:
###A Novel Method to Reduce Time Investment When Processing Videos from Camera Trap Studies###

#Import Libraries
import cv2 
import numpy as np
import argparse
import os
from shapely.ops import cascaded_union
import shapely.geometry as sg

#Define command line arguments
parser = argparse.ArgumentParser()

#Video file
parser.add_argument("-f", help="path of single video",type=str,default="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv")
#threshold for variance
parser.add_argument("-t", help="threshold",type=int)

f="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv"
#f ='C:/Users/Ben/Desktop/MeerkatTest/smallshark.avi'
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
rawsize=[]
frame_counter=0

while (1):
    #Capture next frame, if there is no next frame; break.
    ret,img = cap.read()
    rawsize.append(img)
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

vidname=os.path.join(dest,flname,"Difference.avi")

codec=cv2.VideoWriter_fourcc('X','V','I','D')
out = cv2.VideoWriter(vidname,codec,4,(height,width),True)                

print(out.isOpened())

for i in diff_holder:
    out.write(i)
        
# Release everything if job is finished
out.release()
print(out.isOpened())

print("done")

#how many are above a threshold?
above_threshold = []
for i in diff_holder:
    ret,grey_image = cv2.threshold(i, 50, 255, cv2.THRESH_BINARY )
    if np.sum(grey_image) > 0: 
        print np.sum(grey_image)
        above_threshold.append(grey_image)

vidname=os.path.join(dest,flname,"ThresholdDifference.avi")

codec=cv2.VideoWriter_fourcc('X','V','I','D')
out = cv2.VideoWriter(vidname,codec,5,(heightr,widthr),False)                

print(out.isOpened())

for i in above_threshold: out.write(i)
        
#draw bounding boxes around points
bounding_s=[]
for i in range(1,len(diff_holder)):
    _,contours,hierarchy = cv2.findContours(diff_holder[i].copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE ) 
    for cnt in contours:
            bounding_rect = cv2.boundingRect( cnt )
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(rawsize[i],(x,y),(x+w,y+h),(0,0,255),2)
    
vidname=os.path.join(dest,flname,"BoundingS.avi")

codec=cv2.VideoWriter_fourcc('X','V','I','D')
out = cv2.VideoWriter(vidname,codec,4,(heightr,widthr),False)                

print(out.isOpened())

for i in rawsize: out.write(i)
        
        
###Compare with MotionMeerkat
#############################
##Contour Analysis and Post-Proccessing
#############################
cap=cv2.VideoCapture(f)

ret,display_image=cap.read()
#initial paramaters
grey_image = np.uint8(display_image)
running_average_image = np.float32(display_image)
running_average_in_display_color_depth = display_image.copy()
difference =  display_image.copy()
accAvg=0.35
threshT=50

top = 0
bottom = 1
left = 0
right = 1


#collect outputs
out_collection =[]

cap=cv2.VideoCapture(f)


while (1):
    #Capture next frame, if there is no next frame; break.
    ret,img = cap.read()
    frame_counter=frame_counter+1
    if not ret:
        break
    
    # Create an image with interactive feedback:
    display_image = img.copy()
    
    # Create a working "color image" to modify / blur
    color_image =  display_image.copy()
    
    # Use the Running Average as the static background
    cv2.accumulateWeighted(color_image,running_average_image,accAvg)                                  
    running_average_in_display_color_depth = cv2.convertScaleAbs(running_average_image)
                               
    # Subtract the current frame from the moving average.
    difference=cv2.absdiff( color_image, running_average_in_display_color_depth)
        
    # Convert the image to greyscale.
    grey_image=cv2.cvtColor( difference,cv2.COLOR_BGR2GRAY)
    
    # Threshold the image to a black and white motion mask:
    ret,grey_image = cv2.threshold(grey_image, 50, 255, cv2.THRESH_BINARY )
    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    grey_image= cv2.morphologyEx(grey_image, cv2.MORPH_OPEN, kernel)  
    
    points = []   # Was using this to hold camera_imageROIeither pixel coords or polygon coords.
    bounding_box_list = []
    
    # Now calculate movements using the white pixels as "motion" data
    _,contours,hierarchy = cv2.findContours(grey_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
                
    
    print(len(contours))
    if len(contours) == 0 :
        continue
    
    cnt=contours[0]
            
    drawing = np.uint8(display_image)
                
    for cnt in contours:
            bounding_rect = cv2.boundingRect( cnt )
            point1 = ( bounding_rect[0], bounding_rect[1] )
            point2 = ( bounding_rect[0] + bounding_rect[2], bounding_rect[1] + bounding_rect[3] )
            bounding_box_list.append( ( point1, point2 ) )
            
    # Find the average size of the bbox (targets), then
    # remove any tiny bboxes (which are probably just noise).
    # "Tiny" is defined as any box with 1/10th the area of the average box.
    # This reduces false positives on tiny "sparkles" noise.
    box_areas = []
    for box in bounding_box_list:
            box_width = box[right][0] - box[left][0]
            box_height = box[bottom][0] - box[top][0]
            box_areas.append( box_width * box_height )
            
    average_box_area = 0.0
    if len(box_areas): average_box_area = float( sum(box_areas) ) / len(box_areas)
    
    trimmed_box_list = []
    for box in bounding_box_list:
            box_width = box[right][0] - box[left][0]
            box_height = box[bottom][0] - box[top][0]
            
            # Only keep the box if it's not a tiny noise box:
            if (box_width * box_height) > average_box_area*.3: 
                    trimmed_box_list.append( box )
    
    #shapely does a much faster job of polygon union
    #format into shapely bounding feature
    shape_list=[]
    
    ## Centroids of each target
    bound_center=[]
    
    for out in trimmed_box_list:
            sh_out=sg.box(out[0][0],out[0][1],out[1][0],out[1][1])
            shape_list.append(sh_out)
    
    #shape_pol=sg.MultiPolygon(shape_list)
    casc=cascaded_union(shape_list).buffer(1)
    
    if casc.type=="MultiPolygon":
        #draw shapely bounds
        for p in range(1,len(casc.geoms)):
            b=casc.geoms[p].bounds
            if casc.geoms[p].area > ((width * height) * (float(0.1/100))):
                    cv2.rectangle(img,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=2)
                    #Return the centroid to list, rounded two decimals
                    x=round(casc.geoms[p].centroid.coords.xy[0][0],2)
                    y=round(casc.geoms[p].centroid.coords.xy[1][0],2)
                    bound_center.append((x,y)) 
    else:
            b=casc.bounds
            #If bounding polygon is larger than the minsize, draw a rectangle
            if casc.area > ((width * height) * (float(0.1/100))):
                    cv2.rectangle(img,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=3)
                    x=round(casc.centroid.coords.xy[0][0],2)
                    y=round(casc.centroid.coords.xy[1][0],2)
                    bound_center.append((x,y))  

    out_collection.append(img)


vidname=os.path.join(dest,flname,"MeerkatResultAccAvg.avi")

height=int(cap.get(3))
width=int(cap.get(4))

codec=cv2.VideoWriter_fourcc('X','V','I','D')
out = cv2.VideoWriter(vidname,codec,3,(height,width),True)    

print(out.isOpened())

for i in  out_collection: out.write(i)
            
               
