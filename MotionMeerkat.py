#!/usr/bin/env python

Usage = """

Welcome to MotionMeerkat!

Automated capture of motion frames from a video file.

For help, see the wiki: https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki

Default values for parameters are in parenthesis. To select default hit enter.

Affirmative answers to questions are y, negative answers n

Please use double quotes for file paths, but no quotes for any other responses. 

"""
import cv2
import numpy as np
import time
import sys, os, random, hashlib
import re
from math import *
import glob
from datetime import datetime, timedelta
import csv
import argparse
from shapely.ops import cascaded_union
import shapely.geometry as sg
import traceback
import sourceM
import BackgroundSubtractor
          
###Create motion class with sensible defaults

class Motion:

        def __init__(self):
                #Empty list for time stamps
                self.stamp=[]

                #Write header row
                self.stamp.append(("Time","Frame","X","Y"))
                #Empty list for area counter
                self.areaC=[]
                self.areaC.append(("Time","Frame","X","Y"))

        #If there were system arguments
                self.parser = argparse.ArgumentParser()

                #Read in system arguments if they exist
                if len(sys.argv)< 2:
                        print Usage
                else:
                        self.parser.add_argument("--runtype", help="Batch or single file",default='file')
                        self.parser.add_argument("--batchpool", help="run directory of videos",type=str)
                        self.parser.add_argument("--inDEST", help="path of single video",type=str,default="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv")
                        self.parser.add_argument("--fileD", help="output directory",default="C:/MotionMeerkat")
                        self.parser.add_argument("--subMethod", help="Background Subtraction Method",type=str,default="Acc")                    
                        self.parser.add_argument("--adapt", help="Adaptive background averaging",action='store_true',default=False)
                        self.parser.add_argument("--accAvg", help="Fixed background averaging rate",default=0.35,type=float)
                        self.parser.add_argument("--frameHIT", help="expected percentage of motion frames",default=0.1,type=float)
                        self.parser.add_argument("--floorvalue", help="minimum background averaging",default=0.01,type=float)
                        self.parser.add_argument("--threshT", help="Threshold of movement",default=30,type=int)
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
                                
                                
        ###########Inputs Read in #################

        #define video function
        #Find path of jpegs

        def videoM(self):
                if self.makeVID not in ("video","both"):
                        return("")
                
                normFP=os.path.normpath(self.inDEST)
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
                cap = cv2.VideoCapture(self.inDEST)

                        #Get frame rate if the plotwatcher setting hasn't been called
                        # not the most elegant solution, but get global frame_rate
                if not self.frameSET:
                        fr=round(cap.get(5))
                else:
                        fr=self.frame_rate

                orig_image = cap.read()[1]  

                ###Get information about camera and image
                width = np.size(orig_image, 1)
                height = np.size(orig_image, 0)
                frame_size=(width, height)                      

                # Define the codec and create VideoWriter object
                fourcc = cap.get(6)
                
                out = cv2.VideoWriter(vidDEST,int(fourcc),float(fr), frame_size)                    

                #split and sort the jpg names
                jpgs.sort(key=getint)

                #Loop through every frame and write video
                for f in jpgs:
                        fr=cv2.imread(f)
                        out.write(fr)

                # Release everything if job is finished
                cap.release()
                out.release()

                #If video only, delete jpegs
                if self.makeVID == "video":
                        for f in jpgs:
                                os.remove(f)
                 
        #Define the run function
        def prep(self):
                
                #Report name of file
                sys.stderr.write("Processing file %s\n" % (self.inDEST))
                
                #start timer
                self.start=time.time()
                
                #Define directories, here assuming that we want to append the file structure of the last three folders to the file destination
                normFP=os.path.normpath(self.inDEST)
                (filepath, filename)=os.path.split(normFP)
                (shortname, extension) = os.path.splitext(filename)
                (_,IDFL) = os.path.split(filepath)
                
                #we want to name the output a folder from the output destination with the named extension        
                print("AccAvg begin value is: %s" % (self.accAvg))

                ###########Failure Classes, used to format output and illustrate number of frames
                ##No motion, the frame was not different enough compared to the background due to accAvg 
                self.nodiff=0
                ##No contours, there was not enough motion compared to background, did not meet threshold
                self.nocountr=0
                ###Not large enough, the movement contour was too small to be included 
                self.toosmall=0      
                
                #If its batch, give an extra folder
                if self.runtype == 'batch':
                        file_destination=os.path.join(self.fileD,IDFL,shortname)
                else:
                        file_destination=os.path.join(self.fileD,shortname)
                
                if not os.path.exists(file_destination):
                        os.makedirs(file_destination)
                
                print("Output path will be %s" % (file_destination))
                
                #create hit counter to track number of outputs
                hitcounter=0
                
                #Begin video capture
                cap = cv2.VideoCapture(self.inDEST)
                
                #Get frame rate if the plotwatcher setting hasn't been called
                # not the most elegant solution, but get global frame_rate
                if not self.frameSET:
                                
                        self.frame_rate=round(cap.get(5))
                
                #get frame time relative to start
                frame_time=cap.get(0)     
                
                #get total number of frames
                total_frameC=cap.get(7)     

                sys.stderr.write("frame rate: %s\n" % self.frame_rate)
                
                ####Burnin and first image
                #Count the number of frames returned
                frame_count=0
                self.total_count=0
                
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
                
                #make a copy of the image
                orig_ROI=orig.copy()

                #make a copy for the markup
                iorig=orig.copy()    

                #Set region of interest 
                if self.set_ROI:
                        
                        roi=sourceM.Urect(iorig)
                        
                        if self.ROI_include == "include": display_image=orig_ROI[roi[1]:roi[3], roi[0]:roi[2]]
                        else:
                                orig_ROI[roi[1]:roi[3], roi[0]:roi[2]]=255
                                display_image=orig_ROI                        
                else:
                        display_image=orig              
                        
                width = np.size(display_image, 1)
                height = np.size(display_image, 0)
                frame_size=(width, height)

                ###If set area counter, draw another box.
          
                if self.set_areacounter:
                        area_box=sourceM.Urect(orig,"Set Area Counter")
                
                        #Draw and show the area to count inside
                        cv2.rectangle(orig, (area_box[1],area_box[3]), (area_box[0],area_box[2]), (255,0,0), 1)     
                        
                ############################
                #Initialize Background Subtraction
                ############################
                
                backgr=BackgroundSubtractor.Background(subMethod,orig_image,self.accAvg,self.threshT)
        
                frameC_announce=0
                
                #Set time
                t0 = time.time()

                #Start with motion flag on
                noMotion=False
        
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
                                   
# Define within loop run
def run(self):
        # Capture frame from file
        ret,camera_imageO = cap.read()
        if not ret:
                #finalize the counters for reporting
                self.frame_count=frame_count
                self.file_destination=file_destination
                break
                      
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
        #create iterable for scanner

        #Print trackbar
        #for some videos this capture doesn't work, and we need to ignore frame
        if not total_frameC == 0.0:
                #This is a bit convulted, but because of scanning, we might miss the flag to calculate time, give it a step size equal to scan size
                countR=frame_count - np.arange(0,self.scan+1)
                
                #If percent compelted is a multiple of 10, print processing rate.
                #format frame count to percentage and interger
                numbers = [ round(x/float(total_frameC),3)*100 for x in countR ]
                
                #is frame count a multiple of 10
                if any([x %10 ==0 for x in numbers]):
                        
                        fc=float(frame_count)/total_frameC*100
                        
                        #Give it a pause feature so it doesn't announce twice on the scan, i a bit ugly, but it doesn't run very often.
                        #if the last time the percent complete was printed was within the scan range, don't print again. 
                        if abs(frameC_announce - frame_count) >= self.scan:
                                print("%.0f %% completed" % fc)
                                print( "%.0f candidate motion frames" % total_count)
                                frameC_announce=frame_count                                                
                                
                        #Reset the last time it was printed. 
                        
        ####Adaptively set the aggregate threshold, we know that about 95% of data are negatives. 
        #set floor flag, we can't have negative accAVG
        floor=0
        if self.adapt:
                sourceM.adapt(frame_rate=self.frame_rate,accAvg=self.accAvg,file_destination=file_destination,floorvalue=self.floorvalue) 

        #############################
        ##BACKGROUND SUBTRACTION
        #############################
        grey_image=backgr.BackGroundSub(camera_imageROI)
        
        #############################
        ###Contour filters
        #############################
        
        bound_center=backgr.contourFilter(grey_image)

        if len(bound_center) == 0:
                self.toosmall=self.toosmall+1
                noMotion=True                   
                continue

        #Set flag for inside area
        inside_area=False
        if self.set_areacounter:
        #test drawing center circle
                for box in bound_center:
                        
                        #Do this the simple way for now

                        #is the x coordinate within
                        if area_box[2] > box[0] > area_box[0]:
                                if area_box[3] > box[1] > area_box[1]:
                                                inside_area= not inside_area
                                                if self.ROI_include == "exclude":
                                                        cv2.rectangle(camera_imageO,(area_box[0],area_box[1]),(area_box[2],area_box[3]),(242,221,61),thickness=1,lineType=4)
                                                else:
                                                        cv2.rectangle(display_image,(area_box[0],area_box[1]),(area_box[2],area_box[3]),(242,221,61),thickness=1,lineType=4)
                                                
                                                
        ##################################################
        #Write image to file
        ##################################################
        
        if not self.makeVID == "none":
                if self.makeVID in ("frames","both"):
                        if self.ROI_include == "exclude":
                                cv2.imwrite(file_destination + "/"+str(frame_count)+".jpg",camera_imageO)
                        else:
                                cv2.imwrite(file_destination + "/"+str(frame_count)+".jpg",display_image)
        
        #save the frame count and the time in video, in case user wants to check in the original
        #create a time object, this relies on the frame_rate being correct!
        #set seconds
        sec = timedelta(seconds=int(frame_count/float(self.frame_rate)))             
        d = datetime(1,1,1) + sec

        for target in bound_center:
                stampadd=(str("%d:%d:%d "  % (d.hour,d.minute, d.second)), int(frame_count),target[0],target[1])
                self.stamp.append(stampadd)

        #if inside area and counter is on, write stamp to a seperate file
        if self.set_areacounter & inside_area:
                for target in bound_center:
                        stampadd=(str("%d:%d:%d "  % (d.hour,d.minute, d.second)), int(frame_count),target[0],target[1])
                        self.areaC.append(stampadd)
                
       ##################################################
        #Have a returned counter to balance hitRate
        hitcounter=hitcounter+1
        self.total_count=self.total_count+1
        #set flag to motion
        noMotion=False


                                        
