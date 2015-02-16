import sys
import sourceM
import argparse

Usage = """

Welcome to MotionMeerkat!

Automated capture of motion frames from a video file.

For help, see the wiki: https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki

Default values for parameters are in parenthesis. To select default hit enter.

Affirmative answers to questions are y, negative answers n

Please use double quotes for file paths, but no quotes for any other responses. 

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
                                self.parser.add_argument("--moghistory", help="Length of history for MOG background detector",default=1000,type=int)
                                self.parser.add_argument("--subMethod", help="Accumulated Averaging [Acc] or Mixture of Gaussian [MOG] background method",default='Acc',type=str)                                
                                self.parser.add_argument("--mogvariance", help="Variance in MOG to select background",default=16,type=int)                                
                                self.parser.add_argument("--set_ROI", help="Set region of interest?",action='store_true',default=False)
                                self.parser.add_argument("--ROI_include", help="include or exclude?",default="exclude")
                                self.parser.add_argument("--set_areacounter", help="Set region to count area",action="store_true",default=False)
                                self.parser.add_argument("--makeVID", help="Output images as 'frames','video','both', 'none' ?",default='frames',type=str)
                                self.args = self.parser.parse_args(namespace=self)

                                print "\n"
                                print "\n"
                    
                if(len(sys.argv)< 2):
                                #Batch or single file
                                self.runtype=raw_input("'batch' run or single 'file'? (file):\n")   
                                if not self.runtype: self.runtype="file"
                                
                                if(self.runtype=="file"):
                                                self.inDEST=sourceM.ask_file()
                                                
                                if(self.runtype=="batch"):
                                                self.batchpool=raw_input("Enter folder containing videos:\n")
                                
                                #Destination of file
                                self.fileD=raw_input("File Destination Folder (C:/MotionMeerkat/):\n")   
                                if not self.fileD: self.fileD = "C:/MotionMeerkat/"
                
                                #Sensitivity to movement
                                self.accAvg=sourceM.ask_acc()
                                if not self.accAvg: self.accAvg=0.35
                
                                #thresholding, a way of differentiating the background from movement, higher values (0-255) disregard more motion, lower values make the model more sensitive to motion
                                self.threshT=raw_input("Threshold for movement tolerance\nranging from 0 [all] to 255 [no movement] (30):\n")
                                if not self.threshT: self.threshT = 30
                                else: self.threshT=float(self.threshT)
                
                                #minimum size of contour object
                                self.minSIZE=raw_input("Minimum motion contour size (0.2):\n")
                                if not self.minSIZE: self.minSIZE = 0.2
                                else: self.minSIZE=float(self.minSIZE)
                
                                self.advanced= 'y'==raw_input("Set advanced options? (n) :\n")
                                
                                if self.advanced:
                                                #Set background subtractor
                                                self.subMethod=raw_input("Accumulated Averaging [Acc] or Mixture of Gaussian [MOG] background method? (Acc) :\n")
                                                if not self.subMethod: self.subMethod="Acc"
                                                    
                                                if self.subMethod=="Acc":
                                                                #Should accAVG be adapted every 10minutes based on an estimated hitrate
                                                                self.adapt= 'y'==raw_input("Adapt the motion sensitivity based on hitrate? (n) :\n")      
                                                                
                                                                if self.adapt:
                                                                                self.accAvg=sourceM.ask_acc()
                                                                                if not self.accAvg: self.accAvg = 0.35
                                                                    
                                                                                #Hitrate, the expected % of frames per 10 minutes - this is a helpful adaptive setting that helps tune the model, this will be multiplied the frame_rate
                                                                                self.frameHIT=raw_input("Expected percentage of frames with motion (decimal 0.01):\n")
                                                                                if not self.frameHIT: self.frameHIT = 0.01
                                                                                else: self.frameHIT=float(self.frameHIT)
                                                                                    
                                                                                #Floor value, if adapt = TRUE, what is the minimum AccAVG allowed. If this is unset, and it is a particularly still video, the algorithm paradoically spits out alot of frames, because its trying to find the accAVG that matches the frameHit rate below. We can avoid this by simply placing a floor value for accAVG 
                                                                                self.floorvalue=raw_input("Minimum allowed sensitivity (0.05):\n")
                                                                                if not self.floorvalue: self.floorvalue = 0.05
                                                                                else: self.floorvalue=float(self.floorvalue)
                                                #Still need to set moghistory to pass to argument, even if it isn't used.  
                                                self.moghistory = 500
                                                self.mogvariance = 16
                                                
                                                if self.subMethod=="MOG":
                                                                self.moghistory=raw_input("History of Frames for Gaussian (500):\n")
                                                                if not self.moghistory: self.moghistory = 500                                                                
                                                                self.mogvariance=raw_input("Variance in background threshold (16):\n")                                                
                                                                if not self.mogvariance: self.mogvariance = 500
                                                                self.adapt=False
                                                                
                                               
                                               #Skip initial frames of video, in case of camera setup and shake.       
                                                self.burnin= raw_input("Burn in, skip initial minutes of video (0):\n")
                                                if not self.burnin: self.burnin = 0
                                                else: self.burnin=float(self.burnin)
                    
                                            #Decrease frame rate, downsample
                                                self.scan= raw_input("Scan one of every X frames (0):\n")
                                                if not self.scan: self.scan = 0
                                                else: self.scan=int(self.scan)
                    
                                        #Manually set framerate?
                                                self.frameSET= "y" == raw_input("Set frame rate in fps? (n):\n")
                                                #Set frame rate.
                                                if self.frameSET:
                                                                self.frame_rate = raw_input("frames per second:\n")
                                                else: self.frame_rate=0
                                            
                                        #There are specific conditions for the plotwatcher, because the frame_rate is off, turn this to a boolean       
                                                self.plotwatcher='y'==raw_input("Does this video come from a plotwatcher camera? (n) :\n")
                                                if not self.plotwatcher: self.plotwatcher = False

                                                self.segment='y'==raw_input("Segment image using grabcut? (n) :\n")
                                                if not self.segment: self.segment = False
                                                
                                                #set ROI
                                                self.set_ROI= "y" == raw_input("Subsect the image by selecting a region of interest? (n) :\n")
                                                    
                                                if self.set_ROI:
                                                                self.ROI_include=raw_input("Subregion of interest to 'include' or 'exclude'?:\n")
                                                else: self.ROI_include='exclude'
                            
                                                    #Create area counter by highlighting a section of frame
                                                self.set_areacounter='y'==raw_input("Highlight region for area count? (n) \n")
                                                if not self.set_areacounter: self.set_areacounter=False
                            
                                                #make video by stringing the jpgs back into an avi
                                                self.makeVID=raw_input("Write output as 'video', 'frames','both','none'? (frames):\n")
                                                if not self.makeVID:self.makeVID="frames"
                            
                                else:
                                                self.floorvalue=0
                                                self.frameHIT=0
                                                self.adapt=False
                                                self.makeVID="frames"
                                                self.scan = 0
                                                self.burnin = 0
                                                self.ROI_include='exclude'
                                                self.frameSET=False
                                                self.plotwatcher=False
                                                self.frame_rate=0
                                                self.set_ROI=False
                                                self.set_areacounter=False
                                                self.subMethod="Acc"
                                                self.moghistory = 500
                                                self.mogvariance = 16
                                                self.segment = False