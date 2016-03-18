import sys
import os
import sourceM
import argparse
import numpy as np

def arguments(self):
			
	if self.mode=="auto":

		#Array of movement options, first slider
		q1select=np.arange(0,.16,.03)
		self.moglearning=q1select[int(self.q1)]
		
		#Second slider
		q2select=np.arange(10,40,5)
		self.mogvariance=q2select[int(self.q2)]

		#set runtype
		if os.path.isdir(self.inDEST):
				self.runtype="batch"
				self.batchpool=self.inDEST
		else:
				self.runtype="file"
				
		#Set defaults that weren't specified.
		self.fileD="C:\MotionMeerkat"
		self.frameHIT=0.10
		self.adapt=True
		self.makeVID="frames"
		self.scan = 0
		self.threshT=30
		self.burnin = 0
		self.frameSET=False
		self.frame_rate=0
		self.set_areacounter=False
		self.accAvg = 0.35
		self.subMethod="MOG"
		self.windy = False
		self.todraw=False
		self.remove_singles=False
		self.single_distance = 10
		self.pictures=False
		self.ROI_include='include'
			
	else:
		
		print("\n\n\nEntering manual mode")
		
		#Batch or single file
		self.runtype=raw_input("'batch' run, single video 'file' or folder of ordered 'pictures'? (file):\n")   
		if not self.runtype: self.runtype="file"

		if(self.runtype=="file"):
				self.inDEST=sourceM.ask_file()
				self.pictures=False
		if(self.runtype=="batch"):
				self.batchpool=raw_input("Enter folder containing videos:\n")
				self.pictures=False
		if(self.runtype=="pictures"):
				self.inDEST=raw_input("Filenames need to be chronological order. Enter folder containing pictures:\n")                             
				self.pictures=True
		#Destination of file
		self.fileD=raw_input("File Destination Folder (C:\MotionMeerkat):\n")   
		if not self.fileD: self.fileD = str("C:\MotionMeerkat")

		##Automatic mode or manual
		self.mode=raw_input("'Auto' mode or 'manual'. Auto mode will define settings based on video properties. Manual mode allows greater flexibility. (auto)\n")   
		if not self.mode: self.mode = 'auto'
		if self.mode: self.mode=self.mode.lower()
		
		#Sensitivity to background 
		self.moglearning=raw_input("\nSensitivity to background movement, ranging from 0 [very sensitive] to 1.\nRecommended between 0.05 for still videos and 0.2 for windy videos\nAs learning rate increases, fewer frames will be returned (0.15):\n")
		if not self.moglearning: self.moglearning = 0.15
		self.moglearning=float(self.moglearning)
		
		self.mogvariance=raw_input("Background threshold.\nMotion objects more similar in color to background (such as night or underwater) need a lower threshold. Increase to reduce wind error. (16):\n")
		if not self.mogvariance: 
				self.mogvariance = 16
		else:
				self.mogvariance = int(self.mogvariance)

		#minimum size of contour object
		self.drawSmall='enter'
		self.minSIZE=raw_input("Minimum motion object size\nExpressed as the proportion of the screen.\nFor example, the default (0.3) would ignore objects less than 0.3% of the screen size (0.3):\n")
		if not self.minSIZE: self.minSIZE = float(0.3/100)
		else: self.minSIZE=float(self.minSIZE)/100

		self.advanced= 'y'==raw_input("Set advanced options? (n) :\n")
		
		if self.advanced:
				
				self.adapt= 'y'==raw_input("Adapt the motion sensitivity based on expected frequency of visits? (y) :\n")
				if self.adapt:
		
						#Hitrate, the expected % of frames per 10 minutes - this is a helpful adaptive setting that helps tune the model, this will be multiplied the frame_rate
						self.frameHIT=raw_input("Expected percentage of frames with motion (0.15, i.e 15% of frames returned):\n")
						if not self.frameHIT: self.frameHIT = 0.15
						else: self.frameHIT=float(self.frameHIT)
				else:
						self.frameHIT=1
				
				#background method
				self.subMethod=raw_input("\nAccumulated Averaging [Acc] or Mixture of Gaussian [MOG] background method? \nAcc is faster, MOG is more accurate. (MOG):\n")
				if not self.subMethod: self.subMethod="MOG"
				    
				if self.subMethod=="Acc":
						
						#Sensitivity to movement
						self.accAvg=sourceM.ask_acc()
						if not self.accAvg: self.accAvg=0.35
						
						
						#thresholding, a way of differentiating the background from movement, higher values (0-255) disregard more motion, lower values make the model more sensitive to motion
						self.threshT=raw_input("Threshold for movement tolerance\nRanging from 0 [include any movement] to 255 [include no movement]\nSlow moving animals, like fish, need low thresholds [10].\nFast moving animals, like birds, can have higher thresholds [60] (30):\n")
						if not self.threshT: self.threshT = 30
						else: self.threshT=float(self.threshT)                                                                
		
						#Still need to set moglearning to pass to argument, even if it isn't used.  
						self.moglearning = 0.15
						self.mogvariance = 16
				
				if self.subMethod=="MOG":
						
						print("Default background subtractor MOG selected.")
						self.accAvg = 0.35
						self.threshT = 30
						
																
				#Skip initial frames of video, in case of camera setup and shake.       
				self.windy='y'== raw_input("Cap the number of consecutive frames to reduce wind? (n):\n")
				if not self.windy: self.windy = False
				else: 
						self.windy_min= raw_input("If more than 90% of consecutive frames in X minutes are returned, delete frames. (3):\n")
						if not self.windy_min:
								self.windy_min=float(3.0)
						else:
								self.windy_min=float(self.windy_min)

				#Remove singletons
				self.remove_singles= "y" == raw_input("Remove single frames without neighbors to reduce wind? (n) :\n")
				if self.remove_singles:
						self.single_distance=raw_input("Eliminate frames witin no neighbors within X seconds'? (10):\n")
				else: self.single_distance = 10                                           						
				
				#set ROI
				self.set_ROI= "y" == raw_input("Exclude a portion of the image? (n) :\n")
				if self.set_ROI:
						self.ROI_include=raw_input("Subregion of interest to 'include' or 'exclude'? (include):\n")
				else: self.ROI_include='include'   
				
				#Decrease frame rate, downsample
				self.scan= raw_input("Scan one of every X frames (0):\n")
				if not self.scan: self.scan = 0
				else: self.scan=int(self.scan)
				
				#Skip initial frames of video, in case of camera setup and shake.       
				self.burnin= raw_input("Burn in, skip initial minutes of video (0):\n")
				if not self.burnin: self.burnin = 0
				else: self.burnin=float(self.burnin)
				
				#Draw boxes to highlight motion
				self.todraw='y'==raw_input("Draw red boxes to highlight motion? (n) :\n")
				if not self.todraw: self.todraw = False 
				
				#Manually set framerate?
				self.frameSET= "y" == raw_input("Set frame rate in frames per second? (n):\n")
			
				#Set frame rate.
				if self.frameSET:
						self.frame_rate = raw_input("frames per second:\n")
				else: self.frame_rate=0
				
				#Create area counter by highlighting a section of frame
				self.set_areacounter='y'==raw_input("Highlight region for area count? (n) \n")
				if not self.set_areacounter: self.set_areacounter=False
	    
				#make video by stringing the jpgs back into an avi
				self.makeVID=raw_input("Write output as 'video', 'frames','both','none'? (frames):\n")
				if not self.makeVID:self.makeVID="frames"
	    
		else:
				#Set defaults that weren't specified.
				self.frameHIT=0.10
				self.adapt=True
				self.makeVID="frames"
				self.scan = 0
				self.threshT=30
				self.burnin = 0
				self.ROI_include='include'
				self.frameSET=False
				self.frame_rate=0
				self.set_ROI=False
				self.set_areacounter=False
				self.accAvg = 0.35
				self.subMethod="MOG"
				self.windy = False
				self.todraw=False
				self.remove_singles=False
				self.single_distance = 10
				self.drawSmall = 'enter'
					
			
			
