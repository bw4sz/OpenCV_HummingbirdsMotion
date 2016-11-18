import sys
import os
import sourceM
import argparse
import numpy as np
import glob

def arguments(self):
		
	if self.subMethod=="MOG":
		#Array of movement options, first slider
		q1select=np.arange(0,.16,.03)
		self.moglearning=q1select[int(self.q1)]
		
		#Second slider
		q2select=np.arange(10,40,5)
		self.mogvariance=q2select[int(self.q2)]
		
		#set ACC params, these are ignored
		self.accAvg=0.35
		self.threshT=30
	else:
		#Array of movement options, first slider
		q1select=[0.05,0.1,0.2,0.3,0.4,0.5]
		self.accAvg=q1select[int(self.q1)]
		
		#Second slider
		q2select=[5,15,25,35,45,55]
		self.threshT=q2select[int(self.q2)]	
		
		#set MOG params, these are ignored
		self.moglearning=0.1
		self.mogvariance=16		
	
	#set runtype
	if os.path.isdir(self.inDEST):
		#what's in the directory
		
		#Check for photos
		#File formats
		imagef=["*.jpg","*.jpeg","*.tif","*.tiff","*.png"]
		pathimage=[os.path.join(self.inDEST,x) for x in imagef]
		jpgs=[]
		for ext in pathimage:
			found=glob.glob(ext)
			jpgs.extend(found)			
		if len(jpgs) > 2:
			self.pictures=True
			self.runtype="pictures"			
		else:
			self.runtype="batch"
			self.batchpool=self.inDEST
			self.pictures=False			
	else:
		self.runtype="file"
		self.pictures=False					
