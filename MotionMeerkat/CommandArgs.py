import argparse

def commandargs(self):
    #If there were system argument
    self.parser = argparse.ArgumentParser()

    self.parser.add_argument("--runtype", help="Batch, single file or pictures",default='file')
    self.parser.add_argument("--batchpool", help="run directory of videos",type=str)
    self.parser.add_argument("--inDEST", help="path of single video",type=str,default='C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv')
    self.parser.add_argument("--fileD", help="output directory",default="C:/MotionMeerkat")
    self.parser.add_argument("--adapt", help="Adaptive background averaging",action='store_true',default=True)
    self.parser.add_argument("--accAvg", help="Fixed background averaging rate",default=0.35,type=float)
    self.parser.add_argument("--frameHIT", help="Expected percentage of motion frames",default=0.5,type=float)
    self.parser.add_argument("--threshT", help="Threshold of movement",default=30,type=int)
    self.parser.add_argument("--drawSmall", help="'Draw' or 'enter' object size",type=str,default='enter')
    self.parser.add_argument("--minSIZE", help="Minimum size of contour",default=0.1,type=float)
    self.parser.add_argument("--burnin", help="Delay time",default=0,type=int)
    self.parser.add_argument("--scan", help="Scan one of every X frames for motion",default=0,type=int)
    self.parser.add_argument("--frameSET", help="Set frame_rate?",action='store_true',default=False)
    self.parser.add_argument("--frame_rate", help="frames per second",default=1)
    self.parser.add_argument("--moglearning", help="Speed of MOG background detector, lowering values are more sensitive to movement",default=0.09,type=float)                                
    self.parser.add_argument("--subMethod", help="Accumulated Averaging [Acc] or Mixture of Gaussian [MOG] background method",default='MOG',type=str)                                
    self.parser.add_argument("--mogvariance", help="Variance in MOG to select background",default=25,type=int)                                
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
    
    # Set pictures flag
    if not self.runtype=="pictures":
        self.pictures=False
    else:
        self.pictures=True
    print "\n"
    
    #standardize minimum size as a percent of the frame
    self.minSIZE=float(self.minSIZE)/100
