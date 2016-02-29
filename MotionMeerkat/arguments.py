import sys
import sourceM
import argparse

Usage = """

Welcome to MotionMeerkat!

Automated capture of motion frames from a video file.

For help, see the wiki: https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki

Default values for parameters are in parenthesis. To select default hit enter.

Affirmative answers to questions are y, negative answers n

Please do not use quotes for any responses. 

"""

def arguments(self):
        #If there were system argument
                self.parser = argparse.ArgumentParser()

                #Read in system arguments if they exist
                if len(sys.argv)< 2:
                                print Usage
                else:
                                self.parser.add_argument("--runtype", help="Batch or single file",default='file')
                                self.parser.add_argument("--batchpool", help="run directory of videos",type=str)
                                self.parser.add_argument("--inDEST", help="path of single video",type=str,default='C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv')
                                self.parser.add_argument("--fileD", help="output directory",default="C:/MotionMeerkat")
                                self.parser.add_argument("--adapt", help="Adaptive background averaging",action='store_true',default=True)
                                self.parser.add_argument("--accAvg", help="Fixed background averaging rate",default=0.35,type=float)
                                self.parser.add_argument("--frameHIT", help="expected percentage of motion frames",default=0.05,type=float)
                                self.parser.add_argument("--threshT", help="Threshold of movement",default=30,type=int)
                                self.parser.add_argument("--minSIZE", help="Minimum size of contour",default=0.3,type=float)
                                self.parser.add_argument("--burnin", help="Delay time",default=0,type=int)
                                self.parser.add_argument("--scan", help="Scan one of every X frames for motion",default=0,type=int)
                                self.parser.add_argument("--frameSET", help="Set frame_rate?",action='store_true',default=False)
                                self.parser.add_argument("--frame_rate", help="frames per second",default=1)
				self.parser.add_argument("--moglearning", help="Speed of MOG background detector, lowering values are more sensitive to movement",default=0.15,type=float)                                
				self.parser.add_argument("--learning_wait", help="Wait X minutes to allow MOG to initialize?",default='0.5',type=float)                                		                                
                                self.parser.add_argument("--subMethod", help="Accumulated Averaging [Acc] or Mixture of Gaussian [MOG] background method",default='MOG',type=str)                                
                                self.parser.add_argument("--mogvariance", help="Variance in MOG to select background",default=16,type=int)                                
                                self.parser.add_argument("--set_ROI", help="Set region of interest?",action='store_true',default=False)
				self.parser.add_argument("--windy", help="Enable wind correction",action='store_true',default=False)
				self.parser.add_argument("--windy_min", help="How many minutes of continious movement should be ignored?",default='3',type=int)                                		
				self.parser.add_argument("--remove_singles", help="Remove single frames with no neighbors of a given distance",action='store_true',default=False)
				self.parser.add_argument("--single_distance", help="Eliminate frames witin no neighbors within X seconds",default='10',type=int)                                
                                self.parser.add_argument("--ROI_include", help="include or exclude?",default="exclude")
                                self.parser.add_argument("--set_areacounter", help="Set region to count area",action="store_true",default=False)
                                self.parser.add_argument("--todraw", help="Draw red boxes to highlight motion' ?",action="store_true",default=False)				
                                self.parser.add_argument("--makeVID", help="Output images as 'frames','video','both', 'none' ?",default='frames',type=str)
                                self.args = self.parser.parse_args(namespace=self)
				if not self.runtype=="pictures":
						self.pictures=False
				self.segment = False
                                print "\n"
                                print "\n"
                    
                if(len(sys.argv)< 2):
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
                                #self.mode=raw_input("'auto' mode or 'manual'. Manual mode allows greater flexibility. (auto)\n")   
                                #if not self.mode: self.mode = 'auto'
				
				#if self.mode=='auto':
						#print('''Automatic mode will try to guess the settings based on questions and video characteristics. The settings will be printed in case the user wants to refine using manual mode.''')
						#q1=raw_input("How much background variation [eg. wind, waves, debris] do you expect in your video?\n 1[no movement] to 10 [extreme movement] (3)")
						#q2=raw_input("Draw the size of your smallest object")
						#q3=raw_input("Would you like to set a region of interest to crop based on expected location [ie. flower, nest, bait] (y)")
						#q3=raw_input("Would you like to set a region of interest to crop based on expected location [ie. flower, nest, bait] (y)")
				
				#Sensitivity to background 
				self.moglearning=raw_input("Sensitivity to background movement, ranging from 0 [very sensitive] to 1.\nRecommended between 0.05 for still videos and 0.4 for windy videos\nAs learning rate increases, fewer frames will be returned (0.15):\n")
				if not self.moglearning: self.moglearning = 0.15
				self.moglearning=float(self.moglearning)
				
				self.mogvariance=raw_input("Background threshold.\nMotion objects more similar in color to background (such as night or underwater) need a lower threshold. Increase to reduce wind error. (16):\n")
				if not self.mogvariance: self.mogvariance = 16				
                
                                #minimum size of contour object
                                self.minSIZE=raw_input("Minimum motion contour size\nExpressed as the proportion of the screen.\nFor example, the default (0.3) would ignore objects less than 0.3% of the screen size (0.3):\n")
                                if not self.minSIZE: self.minSIZE = 0.3
                                else: self.minSIZE=float(self.minSIZE)
                
                                self.advanced= 'y'==raw_input("Set advanced options? (n) :\n")
                                
                                if self.advanced:
                                                #background method
                                                self.subMethod=raw_input("\nAccumulated Averaging [Acc] or Mixture of Gaussian [MOG] background method? \nAcc is faster, MOG is more accurate. (MOG):\n")
                                                if not self.subMethod: self.subMethod="MOG"
                                                    
                                                if self.subMethod=="Acc":
								
								#Sensitivity to movement
								self.accAvg=sourceM.ask_acc()
								if not self.accAvg: self.accAvg=0.35
								
                                                                #Should accAVG be adapted every 10minutes based on an estimated hitrate
                                                                self.adapt= 'y'==raw_input("Adapt the motion sensitivity based on expected frequency of visits? (y) :\n")      
                                                                
								#thresholding, a way of differentiating the background from movement, higher values (0-255) disregard more motion, lower values make the model more sensitive to motion
								self.threshT=raw_input("Threshold for movement tolerance\nRanging from 0 [include any movement] to 255 [include no movement]\nSlow moving animals, like fish, need low thresholds [10].\nFast moving animals, like birds, can have higher thresholds [60] (30):\n")
								if not self.threshT: self.threshT = 30
								else: self.threshT=float(self.threshT)                                                                

                                                                if self.adapt:
                                                                    
                                                                                #Hitrate, the expected % of frames per 10 minutes - this is a helpful adaptive setting that helps tune the model, this will be multiplied the frame_rate
                                                                                self.frameHIT=raw_input("Expected percentage of frames with motion (0.04, i.e 4% of frames returned):\n")
                                                                                if not self.frameHIT: self.frameHIT = 0.04
                                                                                else: self.frameHIT=float(self.frameHIT)
		
								#Still need to set moglearning to pass to argument, even if it isn't used.  
								self.moglearning = 0.15
								self.mogvariance = 16
                                                
                                                if self.subMethod=="MOG":
								
								print("Default background subtractor MOG selected.")
								self.accAvg = 0.35
								self.threshT = 30
								
								# Learning wait for mog init
								self.learning_wait= raw_input("Ignore frames in the first X minutes to allow MOG to smoothly initialize. (0)\n")
								if not self.learning_wait: 
										self.learning_wait = 0
                                                                                                             					
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
                                                self.frameHIT=0
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
						self.learning_wait = 0
						
						
