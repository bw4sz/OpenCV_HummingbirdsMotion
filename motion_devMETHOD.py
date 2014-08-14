#!/usr/bin/env python

Usage = """

Welcome to MotionMeerkat!

Automated capture of motion frames from a video file.

For help, see the wiki: https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki

Default values for parameters are in parenthesis. To select default hit enter.

Affirmative answers to questions are 'y', negative answers 'n'

"""
import cv2
import cv2.cv as cv
import numpy as np
import time
from scipy import *
from scipy.cluster import vq
import sys, os, random, hashlib
import re
from math import *
import glob
from datetime import datetime, timedelta
import csv
import argparse

#for py2exe needs manual
from scipy.sparse.csgraph import _validation


##Global variables
# BBoxes must be in the format:
# ( (topleft_x), (topleft_y) ), ( (bottomright_x), (bottomright_y) ) )
top = 0
bottom = 1
left = 0
right = 1

BLUE = [255,0,0]        # rectangle color

##Visualize the frames, this should only be used for testing!
vis=False

#A few hard coded testing variables, only to be used by the developers.
todraw=True
objectEdge=False

#Start time
start=time.time()

#Set globals for mouse map, callback has unique syntax
drawing = False # true if mouse is pressed
drawing_area = False # true if mouse is pressed
roi=[]  
ix,iy = -1,-1
#Global methods

def ask_acc():
        in_accAvg=raw_input("Fixed accumulated averaging (accAvg) sensitivity to motion (0.35):\n")
        if in_accAvg:
                try:
                        out=float(in_accAvg)
                        return(out)
                except Exception, e:
                        print( "Error: accAvg much be a numeric value not character." )
                        ask_acc()
                        
#Combine objects of motion bounding boxes
def merge_collided_bboxes(bbox_list ):
                # For every bbox...
                for this_bbox in bbox_list:
                        
                        # Collision detect every other bbox:
                        for other_bbox in bbox_list:
                                if this_bbox is other_bbox: continue  # Skip self
                                
                                # Assume a collision to start out with:
                                has_collision = True
                                
                                # These coords are in screen coords, so > means 
                                # "lower than" and "further right than".  And < 
                                # means "higher than" and "further left than".
                                
                                # We also inflate the box size by 10% to deal with
                                # fuzziness in the data.  (Without this, there are many times a bbox
                                # is short of overlap by just one or two pixels.)
                                if (this_bbox[bottom][0]*1.1 < other_bbox[top][0]*0.9): has_collision = False
                                if (this_bbox[top][0]*.9 > other_bbox[bottom][0]*1.1): has_collision = False
                                
                                if (this_bbox[right][1]*1.1 < other_bbox[left][1]*0.9): has_collision = False
                                if (this_bbox[left][1]*0.9 > other_bbox[right][1]*1.1): has_collision = False
                                
                                if has_collision:
                                        # merge these two bboxes into one, then start over:
                                        top_left_x = min( this_bbox[left][0], other_bbox[left][0] )
                                        top_left_y = min( this_bbox[left][1], other_bbox[left][1] )
                                        bottom_right_x = max( this_bbox[right][0], other_bbox[right][0] )
                                        bottom_right_y = max( this_bbox[right][1], other_bbox[right][1] )
                                        
                                        new_bbox = ( (top_left_x, top_left_y), (bottom_right_x, bottom_right_y) )
                                        
                                        bbox_list.remove( this_bbox )
                                        bbox_list.remove( other_bbox )
                                        bbox_list.append( new_bbox )
                                        
                                        # Start over with the new list:
                                        return merge_collided_bboxes( bbox_list )
                
                # When there are no collions between boxes, return that list:
                return bbox_list   
        
#define a display function
def display(window,t,image):
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.imshow(window,image)
        cv2.waitKey(t)
        cv2.destroyWindow(window)                        
###Create motion class with sensible defaults

class Motion:

        def __init__(self,name):
                self.name=name
                #Empty list for time stamps
                self.stamp=[]

                #Empty list for area counter
                self.areaC=[]

        #If there were system arguments
                self.parser = argparse.ArgumentParser()

                #Read in system arguments if they exist
                if len(sys.argv)<2:
                        print Usage
                else:
                       self.parser.add_argument("--runtype", help="Batch or single file",default='file')
                       self.parser.add_argument("--batchpool", help="run directory of videos")
                       self.parser.add_argument("--inDEST", help="path of single video",default="C:/Program Files/MotionMeerkat/data/PlotwatcherTest.tlv")
                       self.parser.add_argument("--fileD", help="output directory",default="C:/MotionMeerkat")
                       self.parser.add_argument("--adapt", help="Adaptive background averaging",action='store_true',default=False)
                       self.parser.add_argument("--accAvg", help="Fixed background averaging rate",default=0.35,type=float)
                       self.parser.add_argument("--frameHIT", help="expected percentage of motion frames",default=0.1,type=float)
                       self.parser.add_argument("--floorvalue", help="minimum background averaging",default=0.01,type=float)
                       self.parser.add_argument("--threshT", help="Threshold of movement",default=20,type=int)
                       self.parser.add_argument("--minSIZE", help="Minimum size of contour",default=0.1,type=float)
                       self.parser.add_argument("--burnin", help="Delay time",default=0,type=int)
                       self.parser.add_argument("--scan", help="Scan one of every X frames for motion",default=0,type=int)
                       self.parser.add_argument("--frameSET", help="Set frame_rate?",action='store_true',default=False)
                       self.parser.add_argument("--plotwatcher", help="Camera was a plotwatcher?",action="store_true",default=False)
                       self.parser.add_argument("--frame_rate", help="frames per second",default=0)
                       self.parser.add_argument("--set_ROI", help="Set region of interest?",action='store_true',default=False)
                       self.parser.add_argument("--ROI_include", help="include or exclude?",default="include")
                       self.parser.add_argument("--set_areacounter", help="Set region to count area",action="store_true",default=False)
                       self.parser.add_argument("--makeVID", help="Output images as 'frames','video','both', 'none' ?",default='frames')
                       self.args = self.parser.parse_args(namespace=self)

                       print "\n"
                       print "\n"
                                
        #########################################
        #Get user inputs if no system arguments
        #########################################
        def arguments(self):
                if(len(sys.argv)<=2):
                        #Batch or single file
                        self.runtype=raw_input("'batch' run or single 'file'?:\n")   
                        if not self.runtype: self.runtype="file"
                        if(self.runtype=="file"):
                                self.inDEST=raw_input("Enter video input:\n")
                                if not self.inDEST: self.inDEST = "C:/Program Files/MotionMeerkat/data/PlotwatcherTest.tlv"
                        
                        if(self.runtype=="batch"):
                                self.batchpool=raw_input("Enter folder containing videos:\n")
                        
                        #Destination of file
                        self.fileD=raw_input("File Destination Folder:\n")   
                        if not self.fileD: self.fileD = "C:/MotionMeerkat/"

                        #Sensitivity to movement
                        #Should accAVG be adapted every 10minutes based on an estimated hitrate
                        self.adapt= 'y'==raw_input("Adapt the motion sensitivity based on hitrate?:\n")      
                                
                        if self.adapt:
                                self.accAvg=ask_acc()
                                if not self.accAvg: self.accAvg = 0.35
                                
                                #Hitrate, the expected % of frames per 10 minutes - this is a helpful adaptive setting that helps tune the model, this will be multiplied the frame_rate
                                self.frameHIT=raw_input("Expected percentage of frames with motion (decimal 0.01):\n")
                                if not self.frameHIT: self.frameHIT = 0.01
                                else: self.frameHIT=float(self.frameHIT)
                                
                                #Floor value, if adapt = TRUE, what is the minimum AccAVG allowed. If this is unset, and it is a particularly still video, the algorithm paradoically spits out alot of frames, because its trying to find the accAVG that matches the frameHit rate below. We can avoid this by simply placing a floor value for accAVG 
                                self.floorvalue=raw_input("Minimum allowed sensitivity (0.05):\n")
                                if not self.floorvalue: self.floorvalue = 0.05
                                else: self.floorvalue=float(self.floorvalue)
                        else:
                                self.accAvg=ask_acc()
                                if not self.accAvg: self.accAvg = 0.35

                                #set dummy variable for no adapt
                                self.floorvalue=0
                                self.frameHIT=0
                                
                        #thresholding, a way of differentiating the background from movement, higher values (0-255) disregard more motion, lower values make the model more sensitive to motion
                        self.threshT=raw_input("Threshold for movement tolerance\nranging from 0 [all] to 255 [no movement] (20):\n")
                        if not self.threshT: self.threshT = 20
                        else: self.threshT=float(self.threshT)
                        
                        #minimum size of contour object
                        self.minSIZE=raw_input("Minimum motion contour size (0.1):\n")
                        if not self.minSIZE: self.minSIZE = 0.1
                        else: self.minSIZE=float(minSIZE)
                        
                        #Skip initial frames of video, in case of camera setup and shake.       
                        self.burnin= raw_input("Burn in, skip initial minutes of video (0):\n")
                        if not self.burnin: self.burnin = 0
                        else: self.burnin=float(self.burnin)      
                        
                        #Decrease frame rate, downsample
                        self.scan= raw_input("Scan one of every X frames (0):\n")
                        if not self.scan: self.scan = 0
                        else: self.scan=int(self.scan)
                        
                        #Manually set framerate?
                        self.frameSET= "y" == raw_input("Set frame rate in fps?:\n")
                        
                        #Set frame rate.
                        if self.frameSET:
                                self.frame_rate = raw_input("frames per second:\n")
                                
                        else: self.frame_rate=0
                        
                        #There are specific conditions for the plotwatcher, because the frame_rate is off, turn this to a boolean       
                        self.plotwatcher='y'==raw_input("Does this video come from a plotwatcher camera?:\n")
                        
                        #set ROI
                        self.set_ROI= "y" == raw_input("Subsect the image by selecting a region of interest?:\n")
                        
                        if self.set_ROI:
                                self.ROI_include=raw_input("Subregion of interest to 'include' or 'exclude'?:\n")
                        else: self.ROI_include='exclude'

                        #Create area counter by highlighting a section of frame
                        self.set_areacounter='y'==raw_input("Highlight region for area count? \n")

                        #make video by stringing the jpgs back into an avi
                        self.makeVID=raw_input("Write output as 'video', 'frames','both','none'?:\n")
                        if not self.makeVID: self.makeVID="frames"

        ###########Inputs Read in #################

        #define a sorting function
        def getint(self,name):
                f=os.path.split(name)
                (shortname, extension) = os.path.splitext(f[-1]) 
                return int(shortname)

        #define video function
        #Find path of jpegs

        def videoM(x,makeVID):
                normFP=os.path.normpath(x)
                (filepath, filename)=os.path.split(normFP)
                (shortname, extension) = os.path.splitext(filename)
                (_,IDFL) = os.path.split(filepath)

                #we want to name the output a folder from the output destination with the named extension 
                if self.runtype == 'batch':
                        file_destination=os.path.join(self.fileD,IDFL)
                        file_destination=os.path.join(file_destination,shortname)
                        
                else:
                        file_destination=os.path.join(self.fileD,shortname)

                if self.fileD =='':
                        vidDEST=os.path.join(filepath, shortname,shortname +'.avi')
                else:
                        vidDEST=os.path.join(self.fileD, shortname,shortname +'.avi')

                print("Video output path will be %s" % (vidDEST))

                if not os.path.exists(file_destination):
                        os.makedirs(file_destination)

                #Find all jpegs
                jpgs=glob.glob(os.path.join(file_destination,"*.jpg"))                  

                #Get frame rate and size of images
                cap = cv2.VideoCapture(x)

                        #Get frame rate if the plotwatcher setting hasn't been called
                        # not the most elegant solution, but get global frame_rate
                if not self.frameSET:
                        fr=round(cap.get(cv2.cv.CV_CAP_PROP_FPS))
                else:
                        fr=self.frame_rate

                orig_image = cap.read()[1]  

                ###Get information about camera and image
                width = np.size(orig_image, 1)
                height = np.size(orig_image, 0)
                frame_size=(width, height)                      

                # Define the codec and create VideoWriter object
                fourcc = cv2.cv.CV_FOURCC(*'XVID')
                out = cv2.VideoWriter(vidDEST,fourcc, float(fr), frame_size)                    

                #split and sort the jpg names
                jpgs.sort(key=self.getint)

                #Loop through every frame and write video
                for f in jpgs:
                        fr=cv2.imread(f)
                        out.write(fr)

                # Release everything if job is finished
                cap.release()
                out.release()

                #If video only, delete jpegs
                if makeVID == "video":
                        for f in jpgs:
                                os.remove(f)
                        
        #Define experimental contour segmentation size analysis, this is not available in the executable in version 1.1

        def motionContour(self,img,center_point,this_frame_entity_list,img_draw):
                #find edges
                edges=cv2.Canny(img,100,250)
                kernel = np.ones((1.5,1.5),np.uint8)
                closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                
                #find contours
                contours,hierarchy = cv2.findContours(closing,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                
                #display("contour",3000,closing)

                #sort contours
                cnts = sorted(contours, key = cv2.contourArea, reverse = True)
                
                #for cnt in cnts:
                        #bx,by,bw,bh = cv2.boundingRect(cnt)
                        #cv2.drawContours(img,[cnt],0,(0,255,0),1)   # draw #contours in green color
                    
                #get center_point
                index=0
                found=[]
                for cnt in cnts:
                        dist = cv2.pointPolygonTest(cnt,center_point,False)
                        if dist == 1 :
                                found.append(index)
                                #cv2.drawContours(img,[cnt],-1,(0,255,0),1)   # draw #contours in green color
                                #for entity in this_frame_entity_list:
                                        #c = entity[1]  # RGB color tuple
                                        #cv2.circle(img, center_point,  5, (c[0], c[1], c[2]), 3)
                        index=index+1   
                                        
                #Available contours to choose from.
                foundcnts = [cnts[i] for i in found]
                
                #sort for size one more time, get the smallest one
                cntsF = sorted(foundcnts, key = cv2.contourArea)

                #desired_cnt=cntsF[0]
                #need to remove the largest contour?
                
                #draw that contour to be sure
                #img=camera_imageROI.copy()
                for cnt in cntsF:
                        cv2.drawContours(img_draw,[cnt],0,(0,0,255),1)   # draw #contours in red color

                display("contour",1000,img_draw)
                return img_draw
                
        #Define the run function
        def run(self):
                
                #Report name of file
                sys.stderr.write("Processing file %s\n" % (self.inDEST))
                
                #Define directories, here assuming that we want to append the file structure of the last three folders to the file destination
                normFP=os.path.normpath(self.inDEST)
                (filepath, filename)=os.path.split(normFP)
                (shortname, extension) = os.path.splitext(filename)
                (_,IDFL) = os.path.split(filepath)
                
                #we want to name the output a folder from the output destination with the named extension        
                print("AccAvg begin value is: %s" % (self.accAvg))

                ###########Failure Classes, used to format output and illustrate number of frames
                ##No motion, the frame was not different enough compared to the background due to accAvg 
                nodiff=0
                
                ##No contours, there was not enough motion compared to background, did not meet threshold
                nocountr=0
                
                ###Not large enough, the movement contour was too small to be included 
                toosmall=0      
                
                #Hold all the output frames in an array
                motionFRAMES = []
                #If its batch, give an extra folder
                if self.runtype == 'batch':
                        file_destination=os.path.join(self.fileD,IDFL,shortname)
                else:
                        file_destination=os.path.join(self.fileD,shortname)
                
                if not os.path.exists(file_destination):
                        os.makedirs(file_destination)
                
                print("Output path will be %s" % (file_destination))
                
                # Create a log file with each coordinates

                #create hit counter to track number of outputs
                hitcounter=0
                
                #Begin video capture
                cap = cv2.VideoCapture(self.inDEST)
                
                #Get frame rate if the plotwatcher setting hasn't been called
                # not the most elegant solution, but get global frame_rate
                if not self.frameSET:
                                
                        frame_rate=round(cap.get(cv2.cv.CV_CAP_PROP_FPS))
                
                #get frame time relative to start
                frame_time=cap.get(cv.CV_CAP_PROP_POS_MSEC)     
                
                #get total number of frames
                total_frameC=cap.get(cv.CV_CAP_PROP_FRAME_COUNT)     

                sys.stderr.write("frame rate: %s\n" % self.frame_rate)
                
                ####Burnin and first image
                #Count the number of frames returned
                frame_count=0
                total_count=0
                
                #apply burn in, skip the the first X frames according to user input
                for x in range(1,int(float(self.burnin) * int(self.frame_rate) * 60)): 
                        cap.grab()
                        frame_count=frame_count+1
                        
                print("Beginning Motion Detection")
                #Set frame skip counter if downsampling 
                frameSKIP=0
                
                # Capture the first frame from file for image properties
                orig_image = cap.read()[1]  
                        
                #Have to set global for the callback, feedback welcome. 
                global orig
                
                if self.plotwatcher:
                        #cut off the bottom 5% if the timing mechanism is on the bottom. 
                        orig = orig_image[1:700,1:1280]
                else:
                        orig = orig_image.copy()
                
                #if vis: display("origin", 100, orig)
                
                #make a copy of the image
                orig_ROI=orig.copy()

                #make a copy for the markup
                iorig=orig.copy()    

                #Set region of interest 
                if self.set_ROI:

                        #make a copy of the image.

                        def onmouse(event,x,y,flags,param):
                            global ix,iy,roi,drawing

                            # Draw Rectangle
                            if event == cv2.EVENT_RBUTTONDOWN:
                                drawing = True
                                ix,iy = x,y

                            elif event == cv2.EVENT_MOUSEMOVE:
                                if drawing == True:
                                    cv2.rectangle(iorig,(ix,iy),(x,y),BLUE,-1)
                                    rect = (ix,iy,abs(ix-x),abs(iy-y))

                            elif event == cv2.EVENT_RBUTTONUP:
                                drawing = False
                                cv2.rectangle(iorig,(ix,iy),(x,y),BLUE,-1)
                                rect = (ix,iy,x,y)
                                roi.extend(rect)

                        cv2.namedWindow('image',cv2.CV_WINDOW_AUTOSIZE)
                        cv2.setMouseCallback('image',onmouse)

                        print ("Please draw a single rectangle using right click!")
                        while(1):
                                cv2.namedWindow('image',cv2.CV_WINDOW_AUTOSIZE)                 
                                cv2.imshow('image',iorig)
                                k = cv2.waitKey(1) & 0xFF
                                if k == 27:
                                        break
                        
                        cv2.destroyAllWindows()
                        
                        print(roi)
                        
                        if self.ROI_include == "include": display_image=orig_ROI[roi[1]:roi[3], roi[0]:roi[2]]
                        else:
                                orig_ROI[roi[1]:roi[3], roi[0]:roi[2]]=255
                                display_image=orig_ROI
                        
                        display("newImageNORMAL",3000,display_image)
                        
                        
                else:
                        display_image=orig              
                        
                width = np.size(display_image, 1)
                height = np.size(display_image, 0)
                frame_size=(width, height)

                ###If set area counter, draw another box.
                area_box=[]
                if self.set_areacounter:
                        
                        def onmouse(event,x,y,flags,param):
                            global ix,iy,mode,roi,drawing

                            # Draw Rectangle
                            if event == cv2.EVENT_RBUTTONDOWN:
                                drawing = True
                                ix,iy = x,y

                            elif event == cv2.EVENT_MOUSEMOVE:
                                if drawing == True:
                                    cv2.rectangle(orig,(ix,iy),(x,y),BLUE,-1)
                                    rect = (ix,iy,abs(ix-x),abs(iy-y))

                            elif event == cv2.EVENT_RBUTTONUP:
                                drawing = False
                                cv2.rectangle(orig,(ix,iy),(x,y),BLUE,-1)
                                rect = (ix,iy,abs(ix-x),abs(iy-y))
                                area_box.extend(rect)

                        cv2.namedWindow('image',cv2.CV_WINDOW_AUTOSIZE)
                        cv2.setMouseCallback('image',onmouse)
                        print ("Please draw a single rectangle using right click!")

                        while(1):
                                cv2.namedWindow('image',cv2.CV_WINDOW_AUTOSIZE)                 
                                cv2.imshow('image',orig)
                                k = cv2.waitKey(1) & 0xFF
                                if k == 27:
                                        break
                        
                        cv2.destroyAllWindows()
                        
                        #Draw and show the area to count inside
                        cv2.rectangle(orig, (area_box[1],area_box[3]), (area_box[0],area_box[2]), (255,0,0), 1)     
                        display("Area counter",2000,orig)
                        
                # Greyscale image, thresholded to create the motion mask:
                grey_image = np.uint8(display_image)
                
                # The RunningAvg() function requires a 32-bit or 64-bit image...
                running_average_image = np.float32(display_image)
                
                # ...but the AbsDiff() function requires matching image depths:
                running_average_in_display_color_depth = display_image.copy()
                
                # The difference between the running average and the current frame:
                difference =  display_image.copy()
                
                target_count = 1
                last_frame_entity_list = []
                frameC_announce=0
                
                #Set time
                t0 = time.time()
                
                # Prep for text drawing:
                text_font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX, .5, .5, 0.0, 1, cv.CV_AA )
                text_coord = ( 5, 15 )
                text_color = (255,255,255)

                # Set this to the max number of targets to look for (passed to k-means):
                max_targets = 2
                
                #Start with motion flag on
                noMotion=False

                #Subtraction method
                #submeth="MOG2"
                
                #MOG method creator
                #fgbg = cv2.createBackgroundSubtractorMOG()
                
                while True:
                        
                        #Was the last frame no motion; if not, scan frames
                        if not self.scan ==0:
                                if noMotion:
                                        for x in range(1,self.scan):
                                                cap.grab()
                                                frame_count=frame_count+1
                                else:
                                        pass
                        else:
                                pass
                                        
                        # Capture frame from file
                        ret,camera_imageO = cap.read()
                        if not ret:
                                #finalize the counters for reporting
                                self.frame_count=frame_count
                                self.total_count=total_count
                                self.nodiff=nodiff
                                self.nocountr=nocountr
                                self.toosmall=toosmall
                                self.start=start
                                self.file_destination=file_destination
                                return(motionFRAMES)
                                      
                        #Cut off the bottom 5% if the plotwatcher option is called. 
                        if not self.plotwatcher:
                                camera_image = camera_imageO.copy()     
                        else:
                                camera_image = camera_imageO[1:700,1:1280]
                        
                        #If set roi, subset the image
                        if not self.set_ROI:
                                camera_imageROI=camera_image
                        else:
                                if self.ROI_include == "include":camera_imageROI=camera_image[roi[1]:roi[3], roi[0]:roi[2]]
                                else: 
                                        #Exclude area by making it a white square
                                        camera_imageROI=camera_image.copy()
                                        camera_imageROI[roi[1]:roi[3], roi[0]:roi[2]]=255
                                        
                        frame_count += 1
                        frame_t0 = time.time()
                        
                        #Print trackbar
                        #for some videos this capture doesn't work, and we need to ignore frame
                        if not total_frameC == 0.0:
                                #This is a bit convulted, but because of scanning, we might miss the flag to calculate time, give it a step size equal to scan size
                                countR=frame_count - np.arange(0,self.scan+1)
                                if not self.scan ==0 :a = countR.astype(np.float32, copy=False)
                                else: a = frame_count
                                #If percent compelted is a multiple of 10, print processing rate.
                                if any((a/total_frameC)*100 %10 == 0):
                                        
                                        fc=float(frame_count)/total_frameC*100
                                        #Give it a pause feature so it doesn't announce twice on the scan, i a bit ugly, but it doesn't run very often.
                                        #if the last time the percent complete was printed was within the scan range, don't print again. 
                                        if not 0.0 <= abs(frameC_announce - frame_count) <= self.scan:
                                                print("%.0f %% completed" % fc)
                                                print( "%.0f candidate motion frames" % total_count)
                                                
                                        #tracktime=time.time()
                                        #Reset the last time it was printed. 
                                        frameC_announce=frame_count
                                        
                        ####Adaptively set the aggregate threshold, we know that about 95% of data are negatives. 
                        #set floor flag, we can't have negative accAVG
                        floor=0
                        if self.adapt:
                                        
                                #Every 10min, reset the accAvg threshold, depending on expected level of movement

                                #Should be a integer, round it
                                fift=round(10*60*float(self.frame_rate))
                                
                                if frame_count % fift == 0:  
                                        
                                       #If the total base is fift (10min window), then assuming 99% of images are junk the threshold should be
                                        #We've been counting frames output to file in the hitcounter
                                        print(str(hitcounter) + " files written in last 10minutes" + "\n" )             
                                        if hitcounter > (fift*frameHIT) :
                                                accAvg = accAvg + .05
                                        if hitcounter < (fift*frameHIT) :
                                                accAvg = accAvg - .025
                                                
                                        #In my experience its much more important to drop the sensitivity, than to increase it, so i've make the adapt filter move downwards slower than upwards. 
                                        print(file_destination + str(frame_count) + " accAvg is changed to: " + str(accAvg) + "\n")
                                        
                                        #Write change to log file
                                        
                                        #reset hitcoutner for another fifteen minutes
                                        hitcounter=0
                                                                                        
                                        #Build in a floor, the value can't be negative.
                                        if accAvg < floorvalue:
                                                floor=floor + 1
                                        
                                #Reset if needed.
                                        if floor == 1 :
                                                accAvg=floorvalue

                                                print(file_destination + str(frame_count) + " accAvg is reset to: " + str(self.accAvg))
                                                #Write change to log file

                        # Create an image with interactive feedback:
                        display_image = camera_imageROI.copy()
                        
                        # Create a working "color image" to modify / blur
                        color_image =  display_image.copy()\
                        
                        #if vis: display(Initial,2000,color_image)                    

                        # Smooth to get rid of false positives
                        color_image = cv2.GaussianBlur(color_image,(5,5),0)
                        
                        #if vis: display("Blur", 2000, color_image)
                        
                        # Use the Running Average as the static background
                        cv2.accumulateWeighted(color_image,running_average_image,self.accAvg)                                  
                        running_average_in_display_color_depth = cv2.convertScaleAbs( running_average_image)
                                        
                        #if vis: display("Running Average",5000,running_average_in_display_color_depth)                  
                        
                        # Subtract the current frame from the moving average.
                        difference=cv2.absdiff( color_image, running_average_in_display_color_depth)
                        
                        #if vis: display("difference",5000,difference)
                        
                        # Convert the image to greyscale.
                        grey_image=cv2.cvtColor( difference,cv2.COLOR_BGR2GRAY)
                        
                        #If some difference is 0, jump to next frame
                        if sum(grey_image)==0:
                                nodiff=nodiff+1
                                noMotion=True                   
                                continue
                        
                        # Threshold the image to a black and white motion mask:
                        ret,grey_image = cv2.threshold(grey_image, self.threshT, 255, cv2.THRESH_BINARY )

                        #if vis: display("Threshold",1000,grey_image)
                        
                        points = []   # Was using this to hold either pixel coords or polygon coords.
                        bounding_box_list = []

                        # Now calculate movements using the white pixels as "motion" data
                        contours,hierarchy = cv2.findContours(grey_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
                        
                        if len(contours) == 0 :
                                #No movement, add to counter
                                nocountr=nocountr+1
                                #NoMotion flag
                                noMotion=True
                                continue                    
                        
                        #print(len(contours))
                        cnt=contours[0]
                        len(cnt)
                                
                        drawing = np.uint8(display_image)
                        
                        ##Draw the initial contours
                        #if vis:

                                #for cnt in contours:
                                        #bx,by,bw,bh = cv2.boundingRect(cnt)
                                        #cv2.drawContours(drawing,[cnt],0,(0,255,0),1)   # draw #contours in green color
                                
                                #display("contours", 2000, drawing)
                        
                        for cnt in contours:
                                bounding_rect = cv2.boundingRect( cnt )
                                point1 = ( bounding_rect[0], bounding_rect[1] )
                                point2 = ( bounding_rect[0] + bounding_rect[2], bounding_rect[1] + bounding_rect[3] )
                                bounding_box_list.append( ( point1, point2 ) )
                                #polygon_points = cv2.approxPolyDP( cnt,0.1*cv2.arcLength(cnt,True),True)
                                #approx = cv2.approxPolyDP(cnt,0.1*cv2.arcLength(cnt,True),True)
                                
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
                        
                        #if vis: display("trimmed_box",1000,display_image)
                        
                        ## combine boxes that touch
                        try:       
                                bounding_box_list = merge_collided_bboxes( trimmed_box_list )
                        except Exception, e:
                                print 'Error:',e
                                print 'Box Merge Fail:'
                                continue

                        size_filter_box=[]
                        for box in bounding_box_list:
                                box_width = box[right][0] - box[left][0]
                                box_height = box[bottom][0] - box[top][0]
                                
                                # Only keep the box if its larger than the user specified area
                                if (box_width * box_height) > (width * height) * (float(self.minSIZE)/100):
                                        size_filter_box.append(box)
                                        
                        ## If there are no boxes left at that size, skip to new frame
                        if len(size_filter_box) == 0:
                                toosmall=toosmall+1
                                noMotion=True                   
                                continue                
                        # Draw the merged box list:
                        if todraw:
                                if self.ROI_include == "exclude":
                                        for box in size_filter_box:
                                                cv2.rectangle(camera_imageO, box[0], box[1], (0,255,0), 1 )                     
                                else:
                                        for box in size_filter_box:
                                                cv2.rectangle(display_image, box[0], box[1], (0,255,0), 1 )             
                                                
                        #if vis: display("merged_box",2000,display_image)
                        
                        ##Experimental analysis, no filters yet: Find the segemented object that encompasses the motion pixels
                        ##This uses canny edge detection to capture the whole animal, and would be the first step to size class detection
                                
                        #if objectEdge:
                                #camera_imageO=motionContour(display_image,center_point,this_frame_entity_list,camera_imageO)

                        #Bounding center
                        bound_center=[]
                        ###Get center of the motion contour
                        
                        for box in size_filter_box:
                                mean_x=int(mean((box[0][0],box[1][0])))
                                mean_y=int(mean((box[0][1],box[1][1])))
                                bound_center.append((mean_x,mean_y))

                        #Set flag for inside area
                                inside_area=False
                        if self.set_areacounter:
                        #test drawing center circle
                                for box in bound_center:
                                        
                                        #cv2.circle(camera_imageO,box,5,(255, 255, 0), 3)
                                        #Do this the simple way for now

                                        #is the x coordinate within
                                        if area_box[2] > box[0] > area_box[0]:
                                                if area_box[3] > box[1] > area_box[1]:
                                                                inside_area=invert(inside_area)
     
                        ##################################################
                        #Write image to file
                        ##################################################
                        
                        if not self.makeVID == "none":
                                if self.makeVID == "frames" or "both":
                                        if self.ROI_include == "exclude":
                                                cv2.imwrite(file_destination + "/"+str(frame_count)+".jpg",camera_imageO)
                                        else:
                                                cv2.imwrite(file_destination + "/"+str(frame_count)+".jpg",display_image)

                        
                        #save the frame count and the time in video, in case user wants to check in the original
                        #create a time object, this relies on the frame_rate being correct!
                        #set seconds
                        sec = timedelta(seconds=int(frame_count/float(frame_rate)))             
                        d = datetime(1,1,1) + sec

                        for target in bound_center:
                                stampadd=(str("%d:%d:%d "  % (d.hour,d.minute, d.second)), int(frame_count),target[0],target[1])
                                self.stamp.append(stampadd)

                        #if inside area and counter is on, write stamp to a seperate file
                        if self.set_areacounter & inside_area:
                                for target in bound_center:
                                        stampadd=(str("%d:%d:%d "  % (d.hour,d.minute, d.second)), int(frame_count),
                                                  target[0],target[1])
                                        self.areaC.append(stampadd)
                                
                       ##################################################
                        #Have a returned counter to balance hitRate
                        hitcounter=hitcounter+1
                        total_count=total_count+1
                        #set flag to motion
                        noMotion=False
        
        ########################################
        ###Run Analysis on a Pool of videos
        ########################################
        def wrap(self) :
                #quick error check.
                if self.runtype=="file":
                        if os.path.isfile(self.inDEST): pass
                        else:
                                print("File path does not exist!")
                                time.sleep(2)
                else:
                        if os.path.isdir(self.batchpool): pass
                        else:
                                print("Directory does not exist!")
                                time.sleep(2)

                ###Run Batch Mode                
                if (self.runtype == "batch"):
                        ##Overall destination
                        
                        videoPool= []
                        #Create Pool of Videos
                        for (root, dirs, files) in os.walk(self.batchpool):
                                for files in files:
                                        if files.endswith(".TLV") or files.endswith(".AVI") or files.endswith(".MPG") or files.endswith(".mp4") or files.endswith(".MOD") or files.endswith(".MTS") or files.endswith(".wmv") or files.endswith(".avi"):
                                                videoPool.append(os.path.join(root, files))
                        
                        for vid in videoPool:      
                             
                                #Place run inside try catch loop; in case of error, step to next video
                                ##Run Motion Function
                               
                                try:
                                        motion_frames=run()
                                except Exception, e:
                                        print( "Error %s " % e + "\n" )
                                        time.sleep(8)
                                        print 'Error in Video:',vid
                                #if self.makeVID == "video":
                                        #videoM(self.vid,self.makeVID)

                ###If runtype is a single file - run file destination        
                if (self.runtype == "file"):
                        try:
                                motion_frames=self.run()
                        except Exception, e:
                                print( "Error %s " % e + "\n" )
                                print 'Error in input file:',self.inDEST
                                
                        #if self.makeVID == "video":
                                #self.videoM(self.inDEST,self.makeVID)
        def report(self):
                #Create log file
                log_file_report = self.file_destination + "/" + "Parameters_Results.log"
                log_report = file(log_file_report, 'a' )

                #Print parameters
                #Batch or single file
                log_report.write("\nRun type: %s" % self.runtype)
                if self.runtype=="file":
                        log_report.write("\nInput file path: %s" % self.fileD)
                else:
                        log_report.write("\nInput file path: %s" % self.batchpool)
                log_report.write("\nOutput dir: %s" % self.inDEST)
                log_report.write("\nAdapt accAvg? %s" % self.adapt)
                if self.adapt:
                        log_report.write("\nExpected hitrate: %s" % self.frameHIT)
                        log_report.write("\nMinimum accAvg: %s" % self.floorvalue)
                log_report.write("\nThreshold %s" % self.threshT)
                log_report.write("\nMinimum contour area: %s" % self.minSIZE)
                log_report.write("\nBurnin: %s" % self.burnin)
                log_report.write("\nScan frames: %s" % self.scan)
                if self.frameSET:
                        log_report.write("\nManual framerate: %s" % self.frame_rate)
                if self.set_ROI:
                        log_report.write("\nSet ROI: %s" % self.ROI_include)
                log_report.write("\nArea counter?: %s" % self.set_areacounter)
                log_report.write("\nOutput type?: %s" % self.makeVID)

                #Ending time
                end=time.time()

                #total_time()
                total_min=(end-self.start)/60

                #processed frames per second
                pfps=float(self.frame_count)/(total_min*60)

                ##Write to log file
                log_report.write("Total run time (min): %.2f \n " % total_min)
                log_report.write("Average frames per second: %.2f \n " % pfps)

                #End of program, report some statistic to screen and log
                #log
                log_report.write("\n Thank you for using MotionMeerkat! \n")
                log_report.write("Candidate motion events: %.0f \n " % self.total_count )
                log_report.write("Frames skipped due to AccAvg: %.0f \n " % self.nodiff)
                log_report.write("Frames skipped due to Threshold: %.0f \n " % self.nocountr)
                log_report.write("Frames skipped due to minSIZE: %.0f \n " % self.toosmall)
                log_report.write("Total frames in files: %.0f \n " % self.frame_count)
                rate=float(self.total_count)/self.frame_count*100
                log_report.write("Hitrate: %.2f %% \n" % rate)
                log_report.write("Exiting")

                #print to screen
                print("\n\nThank you for using MotionMeerkat! \n")
                print("Total run time (min): %.2f \n " % total_min)
                print("Average frames processed per second: %.2f \n " % pfps)   
                print("Candidate motion events: %.0f \n " % self.total_count )
                print("Frames skipped due to AccAvg: %.0f \n " % self.nodiff)
                print("Frames skipped due to Threshold: %.0f \n " % self.nocountr)
                print("Frames skipped due to minSIZE: %.0f \n " % self.toosmall)
                print("Total frames in files: %.0f \n " % self.frame_count)

                rate=float(self.total_count)/self.frame_count*100
                print("Hitrate: %.2f %% \n" % rate)

                #Write csv of time stamps and frame counts
                #file name
                time_stamp_report = self.file_destination + "/" + "Frames.csv"

                with open(time_stamp_report, 'wb') as f:
                        writer = csv.writer(f)
                        writer.writerows(self.stamp)
                if self.set_areacounter:
                        area_report = self.file_destination + "/" + "AreaCounter.csv"
                        with open(area_report, 'wb') as f:
                                writer = csv.writer(f)
                                writer.writerows(self.areaC)
                                        

if __name__ == "__main__":
        while True:
                motionVid=Motion("video")
                motionVid.arguments()
                motionVid.wrap()
                motionVid.report()

                #reboot or exit?
                #if system arguments, immediately exit
                if len(sys.argv)>2:
                        break
                ch=raw_input("Press r to reboot, press any key to exit \n")
                if ch=='r':
                    continue
                break
                


