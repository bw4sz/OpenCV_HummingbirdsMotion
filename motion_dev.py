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
import numpy
import sys, os, random, hashlib
import re
from math import *
import glob
from datetime import datetime, timedelta
import csv

#for py2exe needs manual
from scipy.sparse.csgraph import _validation

if len(sys.argv)<2:
        print Usage
else:
        FileList=sys.argv[1:]
        for infileName in FileList:
                print infileName
	
#########################################
#Get user inputs if no system arguments
#########################################

if(len(sys.argv)<=2):
	
	#Batch or single file
	runtype=raw_input("'batch' run or single 'file'?:\n")	
	
        if(runtype=="file"):
                inDEST=raw_input("Enter video input:\n")
        
        if(runtype=="batch"):
                batchpool=raw_input("Enter folder containing videos:\n")
	
	#Destination of file
	fileD=raw_input("File Destination Folder:\n")	
	
	#Sensitivity to movement
	#Should accAVG be adapted every 10minutes based on an estimated hitrate
	adapt= 'y'==raw_input("Adapt the motion sensitivity based on hitrate?:\n")	
		
	if adapt:
		accAvg=raw_input("Accumulated averaging (accAvg) sensitivity to motion starting value (0.35):\n")
		if not accAvg: accAvg = 0.35
		else: accAvg=float(accAvg)
		
		#Hitrate, the expected % of frames per 10 minutes - this is a helpful adaptive setting that helps tune the model, this will be multiplied the frame_rate
		frameHIT=raw_input("Expected percentage of frames with motion (decimal 0.01):\n")
		if not frameHIT: frameHIT = 0.01
		else: frameHIT=float(frameHIT)
		
		#Floor value, if adapt = TRUE, what is the minimum AccAVG allowed. If this is unset, and it is a particularly still video, the algorithm paradoically spits out alot of frames, because its trying to find the accAVG that matches the frameHit rate below. We can avoid this by simply placing a floor value for accAVG 
		floorvalue=raw_input("Minimum allowed sensitivity (0.05):\n")
		if not floorvalue: floorvalue = 0.05
		else: floorvalue=float(floorvalue)
	else:
		accAvg=raw_input("Fixed accumulated averaging (accAvg) sensitivity to motion (0.35):\n")
		if not accAvg: accAvg = 0.35
		else: accAvg=float(accAvg)
		
		#set dummy variable for no adapt
		floorvalue=0
		frameHIT=0
		
	#thresholding, a way of differentiating the background from movement, higher values (0-255) disregard more motion, lower values make the model more sensitive to motion
	threshT=raw_input("Threshold for movement tolerance\nranging from 0 [all] to 255 [no movement] (20):\n")
	if not threshT: threshT = 20
	else: threshT=float(threshT)
	
	#minimum size - use with caution
	minSIZE=raw_input("Minimum motion contour size (0.001):\n")
	if not minSIZE: minSIZE = 0.001
	else: minSIZE=float(minSIZE)
	
	#Skip initial frames of video, in case of camera setup and shake. 	
	burnin= raw_input("Burn in, skip initial minutes of video (0):\n")
	if not burnin: burnin = 0
	else: burnin=float(burnin)	
	
	#Decrease frame rate, downsample
	scan= raw_input("Scan one of every X frames (0):\n")
	if not scan: scan = 0
	else: scan=int(scan)
	
	#Manually set framerate
	frameSET= "y" == raw_input("Set frame rate in fps?:\n")
	
	#Set frame rate?
	if frameSET:
		frame_rate = raw_input("frames per second:\n")
		
	else: frame_rate=0
	
	#There are specific conditions for the plotwatcher, because the frame_rate is off, turn this to a boolean	
	plotwatcher='y'==raw_input("Does this video come from a plotwatcher camera?:\n")
	
	#set ROI
	set_ROI= "y" == raw_input("Subsect the image by selecting a region of interest (ROI)?:\n")
	
	#make video by stringing the jpgs back into an avi
	makeVID="y"==raw_input("Make video out of the resulting frames?:\n")
	
##Visualize the frames, this should only be used for testing!
vis=False

#A few hard coded testing variables, only to be used by the developers.
todraw=True
objectEdge=False

toWrite=False

#Start time
start=time.time()

#Set globals for mouse map, callback has unique syntax
drawing = False # true if mouse is pressed
roi=[]	
ix,iy = -1,-1

###########Inputs Read in #################

# BBoxes must be in the format:
# ( (topleft_x), (topleft_y) ), ( (bottomright_x), (bottomright_y) ) )
top = 0
bottom = 1
left = 0
right = 1

def merge_collided_bboxes( bbox_list ):
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
	
#define a sorting function
def getint(name):
	f=os.path.split(name)
	(shortname, extension) = os.path.splitext(f[-1]) 
	return int(shortname)

#define video function
#Find path of jpegs
def videoM(x,motion_frames):

	normFP=os.path.normpath(x)
	(filepath, filename)=os.path.split(normFP)
	(shortname, extension) = os.path.splitext(filename)
	(_,IDFL) = os.path.split(filepath)
		
	#we want to name the output a folder from the output destination with the named extension 
	if runtype == 'batch':
		file_destination=os.path.join(fileD,IDFL,shortname)
        else:
		file_destination=os.path.join(fileD,shortname)

	if fileD =='':
		vidDEST=os.path.join(filepath, shortname,shortname +'.avi')
	else:
		vidDEST=os.path.join(fileD, shortname,shortname +'.avi')
	
	print("Video output path will be %s" % (vidDEST))
	
	if not os.path.exists(file_destination):
		os.makedirs(file_destination)

#Get frame rate and size of images
	cap = cv2.VideoCapture(x)

		#Get frame rate if the plotwatcher setting hasn't been called
		# not the most elegant solution, but get global frame_rate
	if not frameSET:
		fr=round(cap.get(cv2.cv.CV_CAP_PROP_FPS))
	else:
		fr=frame_rate

	orig_image = cap.read()[1]  

	###Get information about camera and image
	width = np.size(orig_image, 1)
	height = np.size(orig_image, 0)
	frame_size=(width, height)		
	
	# Define the codec and create VideoWriter object
	fourcc = cv2.cv.CV_FOURCC(*'XVID')
	out = cv2.VideoWriter(vidDEST,fourcc, float(fr), frame_size)			
	
	#Loop through every frame and write video
	for f in motion_frames:
		out.write(f)
	
	# Release everything if job is finished
	out.release()
	cap.release()

#Define experimental contour segmentation size analysis, this is not available in the executable in version 1.1

def motionContour(img,center_point,this_frame_entity_list,img_draw):
	#find edges
	edges=cv2.Canny(img,200,250)
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

#Define reporting function to be called at the end of run
def report(frame_count,log_file,total_count,nodiff,nocountr,toosmall,start):
	
	#Ending time
	end=time.time()
	
	#total_time()
	total_min=(end-start)/60
	
	#processed frames per second
	pfps=float(frame_count)/(total_min*60)
	
	##Write to log file
	
	log_file.write("Total run time (min): %.2f \n " % total_min)
	log_file.write("Average frames per second: %.2f \n " % pfps)
	
	log_file.write(str(frame_count) + "Total frames in file:" + "\n" )
	
	#End of program, report some statistic to screen and log
	#log
	log_file.write("\n \n Thank you for using MotionMeerkat! \n")
	log_file.write("Candidate motion events: %.0f \n " % total_count )
	log_file.write("Frames skipped due to AccAvg: %.0f \n " % nodiff)
	log_file.write("Frames skipped due to Threshold: %.0f \n " % nocountr)
	log_file.write("Frames skipped due to minSIZE: %.0f \n " % toosmall)
	log_file.write("Total frames in files: %.0f \n " % frame_count)
	rate=float(total_count)/frame_count*100
	log_file.write("Hitrate: %.2f %% \n" % rate)
	log_file.write("Exiting")
	
	#print to screen
	print("Thank you for using MotionMeerkat! \n")
	print("Total run time (min): %.2f \n " % total_min)
	print("Average frames processed per second: %.2f \n " % pfps)	
	print("Candidate motion events: %.0f \n " % total_count )
	print("Frames skipped due to AccAvg: %.0f \n " % nodiff)
	print("Frames skipped due to Threshold: %.0f \n " % nocountr)
	print("Frames skipped due to minSIZE: %.0f \n " % toosmall)
	print("Total frames in files: %.0f \n " % frame_count)
	
	rate=float(total_count)/frame_count*100
	print("Hitrate: %.2f %% \n" % rate)
	print("Exiting")
	time.sleep(5)
	
#Define the run function
def run(fP,accAvg,threshT,frame_rate,burnin,minSIZE,set_ROI,plotwatcher,frameHIT,floorvalue,adapt,scan):
	
        #Report name of file
        sys.stderr.write("Processing file %s\n" % (fP))
        
        #Define directories, here assuming that we want to append the file structure of the last three folders to the file destination
	normFP=os.path.normpath(fP)
	(filepath, filename)=os.path.split(normFP)
	(shortname, extension) = os.path.splitext(filename)
	(_,IDFL) = os.path.split(filepath)
	
	#we want to name the output a folder from the output destination with the named extension        
        print("Output path will be %s/%s/%s" % (fileD,IDFL,shortname))
        print("AccAvg begin value is: %s" % (accAvg))

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
	if runtype == 'batch':
		file_destination=os.path.join(fileD,IDFL,shortname)
        else:
		file_destination=os.path.join(fileD,shortname)
	
        if not os.path.exists(file_destination):
                os.makedirs(file_destination)
                     
        # Create a log file with each coordinate
        log_file_name = file_destination + "/" + "tracker_output.log"
        log_file = file(log_file_name, 'a' )

        #create hit counter to track number of outputs
	hitcounter=0
	
	#Begin video capture
        cap = cv2.VideoCapture(fP)
        
        #Get frame rate if the plotwatcher setting hasn't been called
	# not the most elegant solution, but get global frame_rate
	if not frameSET:
			
		frame_rate=round(cap.get(cv2.cv.CV_CAP_PROP_FPS))
	
        #get frame time relative to start
        frame_time=cap.get(cv.CV_CAP_PROP_POS_MSEC)     
	
	#get total number of frames
        total_frameC=cap.get(cv.CV_CAP_PROP_FRAME_COUNT)     

        sys.stderr.write("frame rate: %s\n" % frame_rate)
	
	####Burnin and first image
	#Count the number of frames returned
        frame_count=0
	total_count=0
	
	#apply burn in, skip the the first X frames according to user input
	for x in range(1,int(float(burnin) * int(frame_rate) * 60)): 
		cap.grab()
		frame_count=frame_count+1
	#Set frame skip counter if downsampling	
	frameSKIP=0
	
	# Capture the first frame from file for image properties
	orig_image = cap.read()[1]  
		
	#Have to set global for the callback, feedback welcome. 
	global orig
	
	if plotwatcher:
		#cut off the bottom 5% if the timing mechanism is on the bottom. 
		orig = orig_image[1:700,1:1280]
	else:
		orig = orig_image
	
	if vis: display("origin", 100, orig)
	
	#make a copy of the image
	orig_ROI=orig.copy()

	#Set region of interest	
	if set_ROI:
		
		# mouse callback function
		def draw_circle(event,x,y,flags,param):
			global ix,iy,mode,roi,drawing
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
					print(roi)
					k=27
			     
		cv2.namedWindow('image')
		cv2.setMouseCallback('image',draw_circle)
		
		while(1):
			cv2.imshow('image',orig)
			k = cv2.waitKey(1) & 0xFF
			if k == 27:
				break
		
		cv2.destroyAllWindows()
		
		print(roi)
		display_image=orig_ROI[roi[1]:roi[3], roi[0]:roi[2]]
		cv2.imshow('newImage',display_image)
		cv2.waitKey(2000)
		cv2.destroyAllWindows()
	else:
		display_image=orig		
		
	width = np.size(display_image, 1)
	height = np.size(display_image, 0)
	frame_size=(width, height)	
        
        # Greyscale image, thresholded to create the motion mask:
        grey_image = np.uint8(display_image)
        
        # The RunningAvg() function requires a 32-bit or 64-bit image...
        running_average_image = np.float32(display_image)
        
        # ...but the AbsDiff() function requires matching image depths:
        running_average_in_display_color_depth = display_image.copy()
        
        # The difference between the running average and the current frame:
        difference =  display_image.copy()
        
        target_count = 1
        last_target_count = 1
        last_target_change_t = 0.0
        k_or_guess = 1
        codebook=[]
        last_frame_entity_list = []
        
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
	
        while True:
		
		#Was the last frame no motion; if not, scan frames
		if not scan ==0:
			if noMotion:
				for x in range(1,scan):
					cap.grab()
					frame_count=frame_count+1
			else:
				pass
				
                # Capture frame from file
                ret,camera_imageO = cap.read()
                if not ret:
			report(frame_count,log_file,total_count,nodiff,nocountr,toosmall,start)
			return(motionFRAMES)
                        break    
                              
		#Cut off the bottom 5% if the plotwatcher option is called. 
                if not plotwatcher:
			camera_image = camera_imageO	
		else:
			camera_image = camera_imageO[1:700,1:1280]
		
		#If set roi, subset the image
		if not set_ROI:
			camera_imageROI=camera_image
		else:
			camera_imageROI=camera_image[roi[1]:roi[3], roi[0]:roi[2]]
			
                frame_count += 1
                frame_t0 = time.time()
                
		#Print trackbar
		#for some videos this capture doesn't work, and we need to ignore frame
		if not total_frameC == 0.0:		
			if(frame_count/total_frameC*100 %5 == 0):
				fc=frame_count/total_frameC*100
				print("%.0f %% completed" % fc)
				print( "%.0f candidate motion frames" % total_count)
				tracktime=time.time()
				
				#track time in minutes
				trackmin=(tracktime-start)/60
				timetogo=(trackmin / (fc/100))
				print( "Estimated hours remaining %.2f" % timetogo)
				
                ####Adaptively set the aggregate threshold, we know that about 95% of data are negatives. 
		#set floor flag, we can't have negative accAVG
		floor=0
		if adapt:
				
			#Every 10min, reset the accAvg threshold, depending on expected level of movement

			#Should be a integer, round it
			fift=round(10*60*float(frame_rate))
			
			if frame_count % fift == 0:  
				
			       #If the total base is fift (15min window), then assuming 99% of images are junk the threshold should be
				#We've been counting frames output to file in the hitcounter
				log_file.write(str(hitcounter) + "files written in last 10minutes" + "\n" )
				print(str(hitcounter) + " files written in last 10minutes" + "\n" )		
				if hitcounter > (fift*frameHIT) :
					accAvg = accAvg + .05
				if hitcounter < (fift*frameHIT) :
					accAvg = accAvg - .025
					
				#In my experience its much more important to drop the sensitivity, than to increase it, so i've make the adapt filter move downwards slower than upwards. 
				print(file_destination + str(frame_count) + " accAvg is changed to: " + str(accAvg) + "\n")
				
				#Write change to log file
				log_file.write( file_destination + str(frame_count) + " accAvg is changed to: " + str(accAvg) + "\n" )
				
				#reset hitcoutner for another fifteen minutes
				hitcounter=0
										
				#Build in a floor, the value can't be negative.
				if accAvg < floorvalue:
					floor=floor + 1
				
			#Reset if needed.
				if floor == 1 :
					accAvg=floorvalue

					print(file_destination + str(frame_count) + " accAvg is reset to: " + str(accAvg))
					#Write change to log file
					log_file.write( file_destination + str(frame_count) + " accAvg is reset to: " + str(accAvg) + "\n" )

		
                # Create an image with interactive feedback:
                display_image = camera_imageROI.copy()
                
                # Create a working "color image" to modify / blur
                color_image =  display_image.copy()\
		
		if vis: display(Initial,2000,color_image)                    

                # Smooth to get rid of false positives
                color_image = cv2.GaussianBlur(color_image,(5,5),0)
                
                if vis: display("Blur", 2000, color_image)
                
                # Use the Running Average as the static background                                       
                cv2.accumulateWeighted(color_image,running_average_image,accAvg)                                  
                running_average_in_display_color_depth = cv2.convertScaleAbs( running_average_image)
                
                if vis: display("Running Average",5000,running_average_in_display_color_depth)                  
                
                # Subtract the current frame from the moving average.
                difference=cv2.absdiff( color_image, running_average_in_display_color_depth)
                
                if vis: display("difference",5000,difference)
                
                # Convert the image to greyscale.
                grey_image=cv2.cvtColor( difference,cv2.COLOR_BGR2GRAY)
                
		#If some difference is 0, jump to next frame
		if sum(grey_image)==0:
			nodiff=nodiff+1
			noMotion=True			
			continue
		
                # Threshold the image to a black and white motion mask:
                ret,grey_image = cv2.threshold(grey_image, threshT, 255, cv2.THRESH_BINARY )
		
		if vis: display("Threshold",1000,grey_image)
                              
                #non_black_coords_array = numpy.where( grey_image > 3 )
                ## Convert from numpy.where()'s two separate lists to one list of (x, y) tuples:
                #non_black_coords_array = zip( non_black_coords_array[1], non_black_coords_array[0] )
                
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
                if vis:

			for cnt in contours:
				bx,by,bw,bh = cv2.boundingRect(cnt)
				cv2.drawContours(drawing,[cnt],0,(0,255,0),1)   # draw #contours in green color
			
			display("contours", 2000, drawing)
                
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
			#Relative to the entire frame, only keep box if its larger 
			#than .001 of the frame, reduces the number of tiny blips
                        if (box_width * box_height) > average_box_area*.3:
				if (box_width * box_height) > (width * height) * float(minSIZE): 
					trimmed_box_list.append( box )
		
		## If there are no boxes left at that size, skip to new frame
		if len(trimmed_box_list) == 0:
			toosmall=toosmall+1
			noMotion=True			
			continue
		
                ## Draw the trimmed box list:
                #print(len(trimmed_box_list))
                #for box in trimmed_box_list:
		#	cv2.rectangle(camera_imageO, box[0], box[1], (0,255,0), 3 )
		
		if vis: display("trimmed_box",1000,display_image)
                
                ## combine boxes that touch
                try:       
			bounding_box_list = merge_collided_bboxes( trimmed_box_list )
                except Exception, e:
                        print 'Error:',e
                        print 'Box Merge Fail:'
                        continue                
                # Draw the merged box list:
		if todraw:
			for box in bounding_box_list:
				cv2.rectangle(camera_imageO, box[0], box[1], (0,255,0), 1 )			
                
                if vis: display("merged_box",2000,display_image)
		
		##Experimental analysis, no filters yet: Find the segemented object that encompasses the motion pixels
			##This uses canny edge detection to capture the whole animal, and would be the first step to size class detection
			
		#if objectEdge:
			#camera_imageO=motionContour(display_image,center_point,this_frame_entity_list,camera_imageO)


                ## Draw the bullseye to screen:
                #for entity in this_frame_entity_list:
                        #center_point = entity[3]
                        #c = entity[1]  # RGB color tuple
                        #cv2.circle(camera_imageO, center_point, 15, (c[0], c[1], c[2]), 1)
                        #cv2.circle(camera_imageO, center_point, 10, (c[0], c[1], c[2]), 2)
                        #cv2.circle(camera_imageO, center_point,  5, (c[0], c[1], c[2]), 3)
                                                     
                
                ##################################################
                #Write image to file
                
                if toWrite:
			cv2.imwrite(file_destination + "/"+str(frame_count)+".jpg",camera_imageO)
		
		#Append to list
		motionFRAMES.append(camera_imageO)
		
		#Log the frame count and the time in video, in case user wants to check in the original
		#create a time object, this relies on the frame_rate being correct!
		#set seconds
		sec = timedelta(seconds=int(frame_count/float(frame_rate)))		
		d = datetime(1,1,1) + sec
		log_file.write( "%d %d:%d:%d " % ( int(frame_count), d.hour,d.minute, d.second) + "\n" )
		#If a file has been written, flush the log to read
		#sys.stdout.flush()
		
		##################################################
                #Have a returned counter to balance hitRate
		hitcounter=hitcounter+1
                total_count=total_count+1
		
######################################################################################################
###Run Analysis on a Pool of videos
######################################################################################################
if (runtype == "batch"):
        ##Overall destination
        
        videoPool= []
        #Create Pool of Videos
        for (root, dirs, files) in os.walk(batchpool):
                for files in files:
                        if files.endswith(".TLV") or files.endswith(".AVI") or files.endswith(".MPG") or files.endswith(".mp4") or files.endswith(".MOD") or files.endswith(".MTS"):
                                videoPool.append(os.path.join(root, files))
        
        for vid in videoPool:      
             
                #Place run inside try catch loop; in case of error, step to next video
                ##Run Motion Function
               
                try:
                        motion_frames=run(fP=vid,accAvg=accAvg,threshT=threshT,frame_rate=frame_rate,burnin=burnin,minSIZE=minSIZE,set_ROI=set_ROI,plotwatcher=plotwatcher,frameHIT=frameHIT,floorvalue=floorvalue,adapt=adapt,scan=scan)
                except Exception, e:
			print( "Error %s " % e + "\n" )
			time.sleep(8)
                        print 'Error in Video:',vid
                if makeVID:
			videoM(vid,motion_frames)     

###If runtype is a single file - run file destination        
if (runtype == "file"):
	try:
		motion_frames=run(fP=inDEST,accAvg=accAvg,threshT=threshT,frame_rate=frame_rate,burnin=burnin,minSIZE=minSIZE,set_ROI=set_ROI,plotwatcher=plotwatcher,frameHIT=frameHIT,floorvalue=floorvalue,adapt=adapt,scan=scan)
	except Exception, e:
		print( "Error %s " % e + "\n" )
		time.sleep(8)
		print 'Error in Video:',inDEST
		
	if makeVID:
		videoM(inDEST,motion_frames)
				
raw_input("Hit any key to exit:")	
time.sleep(2)