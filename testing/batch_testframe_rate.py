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



videoPool= []
#Create Pool of Videos
for (root, dirs, files) in os.walk("C:/Users/Office653-1/Dropbox/VideosforBen/"):
	for files in files:
		if files.endswith(".TLV") or files.endswith(".AVI") or files.endswith(".MPG") or files.endswith(".mp4"):
			videoPool.append(os.path.join(root, files))

for vid in videoPool:      
     
	#Place run inside try catch loop; in case of error, step to next video
	##Run Motion Function
	##The first arguement is the filepath of the video
	##The second argument is the accumlated averaging, higher values are more sensitive to sudden movements
	##The third value is the thresholding, a way of differentiating the background from movement, higher values (0-255) disregard more motion, lower values make the model more sensitive to motion
	try:
		cap = cv2.VideoCapture(vid)
   
		# Capture the first frame from file for image properties
		orig_image = cap.read()[1]  
		
		###Get information about camera and image
	
		width = np.size(orig_image, 1)
		height = np.size(orig_image, 0)
		frame_size=(width, height)
	 
			      
		cv2.imshow("frame",orig_image)
		cv2.waitKey(1000)
		cv2.destroyWindow("frame")
		
			
		frame_rate=cap.get(cv.CV_CAP_PROP_FPS)        
		print(str(vid))
		print("frame rate: " + str(frame_rate))
		sys.stderr.write("frame rate: " + str(frame_rate))
		
	except Exception, e:
		print 'Error:',e
		print 'Video:',vid
		continue  ##    