#!/usr/bin/env python

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
                print("Welcome to MotionMeerkat!\n")
                
        def prep(self):
                
                #Create initial conditions
                
                #report auto settings
                print('Auto settings...')
                print('Background MOG sensitivity set to %.2f' % self.moglearning)  
                print('MOG Variance tolerance set to %d' % self.mogvariance)  
                
                #For debugging, visualize conditions.
                self.vis=False
                if self.vis: self.todraw = True
                
                #Capture average minimum box size for plotting
                self.avg_area = []
                
                #Empty list for time stamps
                self.stamp=[]

                #Write header row
                self.stamp.append(("Time","Frame","X","Y"))
                
                #Empty list for area counter
                self.areaC=[]
                self.areaC.append(("Time","Frame","X","Y"))
                
                self.top = 0
                self.bottom = 1
                self.left = 0
                self.right = 1
                
                #Capture output for wind detection
                self.frame_results=[]
                
                #Failure Classes, used to format output and illustrate number of frames
                #No motion, the frame was not different enough compared to the background due to accAvg 
                self.nodiff=0
                
                ##No contours, there was not enough motion compared to background, did not meet threshold
                self.nocountr=0
                
                ###Not large enough, the movement contour was too small to be included 
                self.toosmall=0 
                
                #Frames removed due to wind
                self.windy_count=0
                
                #Count the number of frames returned
                self.frame_count=0
                self.total_count=0
                
                #Set time and frame constants
                self.frameC_announce=0
    
                #Start with motion flag on
                self.noMotion=False
                
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
                #set original parameters if needed
                if self.subMethod=="Acc":
                        #set an original to reset at the end
                        self.accAvgBegin=self.accAvg
                else:
                        self.moglearningBegin=self.moglearning

                #If its batch, give an extra folder
                if self.runtype == 'batch':
                        self.file_destination=os.path.join(self.fileD,IDFL,shortname)
                else:
                        self.file_destination=os.path.join(self.fileD,shortname)
                
                if not os.path.exists(self.file_destination):
                        os.makedirs(self.file_destination)
                
                print("Output path will be %s" % (self.file_destination))
                
                #########################
                ##Begin video capture
                #########################
                
                if not self.pictures:
                        ##Get Video Properties
                        self.cap = cv2.VideoCapture(self.inDEST)
                        #Get frame rate if the plotwatcher setting hasn't been called
                        # not the most elegant solution, but get global frame_rate
                        if not self.frameSET:
                                        
                                self.frame_rate=round(self.cap.get(5))
                                #This seems to misinterpret just .tlv files
                                if extension in ['.tlv','.TLV']: self.frame_rate=1
                                print("File type is .tlv, setting frame rate to 1 fps")
                        
                        #get frame time relative to start
                        frame_time=self.cap.get(0)     
                        
                        #get total number of frames
                        self.total_frameC=self.cap.get(7)     
                        sys.stderr.write("frame rate: %s\n" % self.frame_rate)
                        
                        #Burnin and first image
                        
                        #apply burn in, skip the the first X frames according to user input
                        for x in range(1,int(float(self.burnin) * int(self.frame_rate) * 60)): 
                                self.cap.grab()
                                self.frame_count=self.frame_count+1
                                
                        print("Beginning Motion Detection\n")
                        
                        #Set frame skip counter if downsampling 
                        frameSKIP=0
                        
                        # Capture the first frame from file for image properties
                        orig_image = self.cap.read()[1] 
                else:
                        #File formats
                        imagef=["*.jpg","*.JPG","*.jpeg","*.tif","*.tiff","*.JPEG","*.png"]
                        pathimage=[os.path.join(self.inDEST,x) for x in imagef]
                        self.jpgs=[]
                        for ext in pathimage:
                                self.jpgs.extend(glob.glob(ext))
                        print('%d pictures found' % len(self.jpgs))
                        orig_image=cv2.imread(self.jpgs[0])
                        self.total_frameC=len(self.jpgs)
                        self.frame_rate=1
                
                #Let the user define area
                if self.drawSmall == 'draw':
                        print('Draw the expected size of the smallest organism of interest\nObjects smaller than this size will be ignored. Be conservative.')
                        
                        #make a copy for the markup
                        ismalldraw=orig_image.copy()
                        minarea=sourceM.Urect(ismalldraw,"Minimize size setting")
                        minarea=minarea[-4:]                        
                        
                        #get area
                        minh,minw =ismalldraw[minarea[1]:minarea[3], minarea[0]:minarea[2]].shape[0:2]
                        ih,iw=orig_image.shape[0:2]
                        
                        #report area
                        objectsize=float(minh*minw)/float(ih*iw)
                        self.minSIZE=objectsize/(3 * self.frame_rate)
                        
                        print('\nExpected object size set to %.2f percent of frame.\n' % (objectsize*100))
                        print('Minimum motion object size set to %.2f percent of frame based on input and frame rate.\n' % (self.minSIZE*100)) 

                #make a copy for the markup
                iorig=orig_image.copy()

                #Set region of interest 
                if self.set_ROI:
                        self.roi_selected=sourceM.Urect(iorig,"Region of Interest")
                        self.roi_selected=self.roi_selected[-4:]
                        if len(self.roi_selected)==0 :
                                raise ValueError('Error: No box selected. Please select an area by right clicking and dragging with your cursor to create a box. Hit esc to exit the window.')
                        if self.ROI_include == "include": 
                                print("Cropping Frame...complete")
                                self.display_image=orig_image[self.roi_selected[1]:self.roi_selected[3], self.roi_selected[0]:self.roi_selected[2]]
                        else:
                                orig_image[self.roi_selected[1]:self.roi_selected[3], self.roi_selected[0]:self.roi_selected[2]]=255
                                self.display_image=orig_image                             
                else:
                        self.display_image=orig_image              
                 
                #show the display image
                if self.set_ROI:
                        cv2.namedWindow("Crop result")
                        cv2.imshow("Crop result", self.display_image)
                        cv2.waitKey(1200) 
                        cv2.destroyAllWindows()
                        
                self.width = np.size(self.display_image, 1)
                self.height = np.size(self.display_image, 0)
                frame_size=(self.height, self.width)
                                
                ###If set area counter, draw another box.
                if self.set_areacounter:
                        self.area_box=sourceM.Urect(orig_image,"Set Area Counter")
                        if len(self.area_box)==0:                                
                                raise ValueError('Error: No box selected. Please select an area by right clicking and dragging with your cursor to create a box. Hit esc to exit the window.')
                        
                        #Draw and show the area to count inside
                        cv2.rectangle(orig_image, (self.area_box[3],self.area_box[0]), (self.area_box[2],self.area_box[1]), (255,0,0), 1)     
                
                ###Background Constructor, create class
                self.BC=BackgroundSubtractor.Background(self.subMethod,self.display_image,self.accAvg,self.threshT,self.mogvariance)
           
######################################################             
##Function to compute background during the video loop
######################################################

        def run(self):

                while True:
                        #Was the last frame no motion; if not, scan frames
                        if not self.scan ==0:
                                if self.noMotion:
                                        for x in range(1,self.scan):
                                                if not self.pictures:
                                                        self.cap.grab()
                                                else:
                                                        current_image=jpgs.pop()
                                                self.frame_count=self.frame_count+1
                                else:
                                        pass
                        else:
                                pass
                                        
                        # Capture frame from file
                        if not self.pictures:
                                ret,current_image = self.cap.read()
                                if not ret:
                                        #If there are no more frames, break, need to reset AccAVG
                                        if self.subMethod=="Acc": 
                                                self.accAvg=self.accAvgBegin
                                        else:
                                                self.moglearning=self.moglearningBegin
                                        break
                        else:
                                if len(self.jpgs)==0:
                                        break
                                else:
                                        current_image=cv2.imread(self.jpgs.pop())
                                        
                        self.frame_count += 1
                        frame_t0 = time.time()
                        #create iterable for scanner
                
                        #Print trackbar
                        #for some videos this capture doesn't work, and we need to ignore frame
                        if not self.total_frameC == 0.0:
                                #This is a bit convulted, but because of scanning, we might miss the flag to calculate time, give it a step size equal to scan size
                                countR=self.frame_count - np.arange(0,self.scan+1)
                                
                                #If percent compelted is a multiple of 10, print processing rate.
                                #format frame count to percentage and interger
                                numbers = [ round(x/float(self.total_frameC),4)*100 for x in countR ]
                                
                                #is frame count a multiple of 10
                                if any([x %10 ==0 for x in numbers]):
                                        
                                        fc=float(self.frame_count)/self.total_frameC*100
                                        
                                        #Give it a pause feature so it doesn't announce twice on the scan, i a bit ugly, but it doesn't run very often.
                                        #if the last time the percent complete was printed was within the scan range, don't print again. 
                                        if abs(self.frameC_announce - self.frame_count) >= self.scan:
                                                print("%.0f %% completed: %.0f candidate motion frames" % (fc, self.total_count))
                                                self.frameC_announce=self.frame_count                                                

                        #############################
                        ###BACKGROUND SUBTRACTION
                        #############################
                        
                        grey_image=self.BC.BackGroundSub(current_image,self.moglearning)
                        if self.vis: sourceM.displayV("Thresholded image",10,grey_image)
                        
                        #If set roi, subset the image
                        if self.set_ROI:
                                
                                if self.ROI_include == "include":
                                        #Crop
                                        mask = np.ones(grey_image.shape, np.bool)
                                        mask[self.roi_selected[1]:self.roi_selected[3], self.roi_selected[0]:self.roi_selected[2]] = False
                                        grey_image[mask]=0
                                        
                                else: 
                                        mask = np.ones(grey_image.shape, np.bool)
                                        mask[self.roi_selected[1]:self.roi_selected[3], self.roi_selected[0]:self.roi_selected[2]] = False
                                        grey_image[~mask]=0
                                        
                        #######################################
                        ##Contour Analysis and Post-Proccessing
                        #######################################
                        
                        points = []   # Was using this to hold camera_imageROIeither pixel coords or polygon coords.
                        bounding_box_list = []
                        
                        # Now calculate movements using the white pixels as "motion" data
                        _,contours,hierarchy = cv2.findContours(grey_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
                        
                        if len(contours) == 0 :
                                #No movement, add to counter
                                self.nocountr=self.nocountr+1
                                
                                #Result was no motion
                                self.frame_results.append(False)
                                
                                #self.noMotion flag
                                self.noMotion=True
                                self.avg_area.append(0)                                                                                                                        
                                continue                    
                        
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
                                box_width = box[self.right][0] - box[self.left][0]
                                box_height = box[self.bottom][0] - box[self.top][0]
                                box_areas.append( box_width * box_height )
                                
                        average_box_area = 0.0
                        if len(box_areas): average_box_area = float( sum(box_areas) ) / len(box_areas)
                        
                        trimmed_box_list = []
                        for box in bounding_box_list:
                                box_width = box[self.right][0] - box[self.left][0]
                                box_height = box[self.bottom][0] - box[self.top][0]
                                
                                # Only keep the box if it's not a tiny noise box:
                                if (box_width * box_height) > average_box_area*.3: 
                                        trimmed_box_list.append( box )
                        
                        #shapely does a much faster job of polygon union
                        #format into shapely bounding feature
                        shape_list=[]
                        
                        ## Centroids of each target and hold on to target blobs
                        bound_center=[]
                        bound_casc_box=[]
                        
                        for out in trimmed_box_list:
                                
                                #shapely needs to boxes as minx, miny, max x maxy
                                minx=out[0][0]
                                miny=out[1][1]
                                maxx=out[1][0]
                                maxy=out[0][1]
                                
                                #make into a tuple
                                sh_out=sg.box(minx,miny,maxx,maxy)
                                shape_list.append(sh_out)
                        
                        #Merge boxes that touch
                        casc=cascaded_union(shape_list).buffer(1)
                        
                        #Make an object to get the average box size
                        sumbox = []
                        
                        if casc.type=="MultiPolygon":
                            #draw shapely bounds
                                for p in range(1,len(casc.geoms)):
                                        b=casc.geoms[p].bounds
                                        
                                        #Numpy origin is top left
                                        #Shapely origin is bottom left 
                                        minx,miny,maxx,maxy=b
                                        
                                        topleft=(int(minx),int(maxy))
                                        bottomright=(int(maxx),int(miny))
                                        
                                        #Append to summary
                                        sumbox.append(casc.geoms[p].area)
                                        if casc.geoms[p].area > ((self.width * self.height) * self.minSIZE):
                                                        if self.todraw: 
                                                                cv2.rectangle(current_image,topleft,bottomright,(0,0,255),thickness=3)

                                                        #Return the centroid to list, rounded two decimals
                                                        x=round(casc.geoms[p].centroid.coords.xy[0][0],2)
                                                        y=round(casc.geoms[p].centroid.coords.xy[1][0],2)
                                                        bound_center.append((x,y))
                                                        bound_casc_box.append(casc.geoms[p])
                        else:
                                b=casc.bounds
                                #get size 
                                sumbox.append(casc.area)
                                
                                #to draw polygon
                                minx,miny,maxx,maxy=b
                                
                                topleft=(int(minx),int(maxy))
                                bottomright=(int(maxx),int(miny))                                

                                #If bounding polygon is larger than the minsize, draw a rectangle
                                if casc.area > ((self.width * self.height) * self.minSIZE):
                                                if self.todraw: 
                                                        cv2.rectangle(current_image,topleft,bottomright,(0,0,255),thickness=3)                                                        
                                                        
                                                x=round(casc.centroid.coords.xy[0][0],2)
                                                y=round(casc.centroid.coords.xy[1][0],2)
                                                bound_center.append((x,y))
                                                bound_casc_box.append(casc)
                        
                        #Get the average size of box
                        self.avg_area.append(np.array(sumbox).max())                                                                                        
                        
                        if len(bound_center) == 0:
                                
                                #mark as too small
                                self.toosmall=self.toosmall+1
                                
                                #record output
                                self.frame_results.append(False)
                                
                                self.noMotion=True                   
                                #Go to next image
                                continue
                                        
                        #Set flag for inside area
                        inside_area=False
                        if self.set_areacounter:
                        #test drawing center circle
                                for box in bound_center:
                                        
                                        #is the x coordinate within
                                        if self.area_box[2] > box[0] > self.area_box[0]:
                                                if self.area_box[3] > box[1] > self.area_box[1]:
                                                                inside_area= not inside_area
                                                                cv2.rectangle(current_image,(self.area_box[3],self.area_box[0]),(self.area_box[2],self.area_box[1]),(242,221,61),thickness=1,lineType=4)
  
                        ##################################################
                        ###############Write image to file################
                        ##################################################
                        
                        if not self.makeVID == "none":
                                if self.makeVID in ("frames","both"):
                                        cv2.imwrite(self.file_destination + "/"+str(self.frame_count)+".jpg",current_image)
 
                                        #Record frame as motion
                                        self.frame_results.append(True)
                                        
                                        #Is it windy?
                                        if self.windy:
                                                
                                                self.windy_threshold = int(self.windy_min * 60 * self.frame_rate)
                                                runs=sum(self.frame_results[self.frame_count-self.windy_threshold:self.frame_count])/float(self.windy_threshold)
                                                if runs > 0.9: 
                                                        print("It is windy!\nDeleting the past %.0f returned frames" % self.windy_threshold)
                                                        
                                                        #reset the record to frames not returned
                                                        self.frame_results[self.frame_count-self.windy_threshold:self.frame_count]=[False] *(self.windy_threshold)
                                                        
                                                        #Delete frames that encompassed that window
                                                        todel=[self.file_destination + "/" + str(s) + ".jpg" for s in range(self.frame_count-self.windy_threshold,self.frame_count)]
                                                        for x in todel: 
                                                                if os.path.exists(x): 
                                                                        self.windy_count=self.windy_count+1
                                                                        os.remove(x)
                                        
                        #save the frame count and the time in video, in case user wants to check in the original
                        #create a time object, this relies on the frame_rate being correct!
                        #set seconds
                        sec = timedelta(seconds=int(self.frame_count/float(self.frame_rate)))             
                        d = datetime(1,1,1) + sec

                        for target in bound_center:
                                stampadd=(str("%d:%d:%d "  % (d.hour,d.minute, d.second)), int(self.frame_count),target[0],target[1])
                                self.stamp.append(stampadd)

                        #if inside area and counter is on, write stamp to a seperate file
                        if self.set_areacounter & inside_area:
                                for target in bound_center:
                                        stampadd=(str("%d:%d:%d "  % (d.hour,d.minute, d.second)), int(self.frame_count),target[0],target[1])
                                        self.areaC.append(stampadd)
                                
                        #Have a returned counter to balance hitRate
                        self.total_count=self.total_count+1
                        
                        #set flag to motion
                        self.noMotion=False
                        
                        ###Adaptation based on current conditions
                        
                        cutoff=int(self.frame_rate * 60 * 10)
                        
                        if self.adapt:
                                
                                #If current frame is a multiple of the 10 minute mark
                                if self.frame_count % cutoff == 0:                                  
                                
                                        #get the last 10 minutes
                                        lastten=self.frame_results[-cutoff:]
                                        
                                        #If more than 20% of frames have been printed.
                                        
                                        if sum(lastten)/float(len(lastten)) > self.frameHIT:  
                                                if self.subMethod == "MOG":
                                                                
                                                        #increase tolerance rate
                                                        self.mogvariance=self.mogvariance+5
                                        
                                                        #add a ceiling
                                                        if self.mogvariance > 50: self.mogvariance = 50
                                                        
                                                        print("Adapting to video conditions: increasing MOG variance tolerance to %d" % self.mogvariance)
                                                        
        
                                                else:                       

                                                        #Increase accumulated averaging
                                                        self.accAvg=self.accAvg+0.05
                                                
                                                        #Build bounds. in a floor, the value can't be negative.
                                                        if self.accAvg < 0.1: self.accAvg=0.1
                                                        if self.accAvg > 0.55: self.accAvg=0.55
                                                        print("Adapting to video conditions: accAvg is changed to: " + str(self.accAvg) + "\n")                                                        
                                        
        def videoM(self):
                
                ## Methods for video writing in the class Motion
                if self.makeVID not in ("video","both"): return("No Video Output")
                                
                normFP=os.path.normpath(self.inDEST)
                (filepath, filename)=os.path.split(normFP)
                (shortname, extension) = os.path.splitext(filename)
                (_,IDFL) = os.path.split(filepath)
                
                #we want to name the output a folder from the output destination with the named extension 
                if self.runtype == 'batch':
                        self.file_destination=os.path.join(self.fileD,IDFL)
                        self.file_destination=os.path.join(self.file_destination,shortname)
                        
                else:
                        self.file_destination=os.path.join(self.fileD,shortname)
                
                if self.fileD =='':
                        vidDEST=os.path.join(filepath, shortname,shortname +'.avi')
                else:
                        vidDEST=os.path.join(self.fileD, shortname,shortname +'.avi')
                
                print("Video output path will be %s" % (vidDEST))
                
                if not os.path.exists(self.file_destination):
                        os.makedirs(self.file_destination)
                
                #Find all jpegs
                jpgs=glob.glob(os.path.join(self.file_destination,"*.jpg"))                  
                
                #Get frame rate and size of images
                if not self.pictures:
                        self.cap = cv2.VideoCapture(self.inDEST)
                                #Get frame rate if the plotwatcher setting hasn't been called
                                # not the most elegant solution, but get global frame_rate
                        if not self.frameSET:
                                fr=round(self.cap.get(5))
                        else:
                                fr=self.frame_rate
                        
                        orig_image = self.cap.read()[1]  
        
                ###Get information about camera and image
                width = np.size(orig_image, 1)
                height = np.size(orig_image, 0)
                frame_size=(width, height)                      
                
                # Define the codec and create VideoWriter object
                fourcc = self.cap.get(6)
                
                out = cv2.VideoWriter(vidDEST,cv2.VideoWriter_fourcc('M','J','P',"G"),float(fr),frame_size)                    
                
                #split and sort the jpg names
                jpgs.sort(key=sourceM.getint)
                
                #Loop through every frame and write video
                for f in jpgs:
                        cf=cv2.imread(f)
                        out.write(cf)
                
                # Release everything if job is finished
                self.cap.release()
                out.release()
                
                #If video only, delete jpegs
                if self.makeVID == "video":
                        for f in jpgs:
                                os.remove(f)