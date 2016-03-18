#!/usr/bin/env python


import traceback
import sys
import numpy as np
import numpy.core.multiarray
import ctypes
import shapely
import cv2
import FileDialog
import GUI

#MotionMeerkat
import CommandArgs
import motionClass
import wrapper

#==================
# MAIN ENTRY POINT
#==================

if __name__ == "__main__":
        while True:
            
                #Read in system arguments if they exist
                if len(sys.argv)> 2:
                        
                        motionVid=motionClass.Motion()                
                        CommandArgs.commandargs(motionVid)
                        wrapper.wrap(motionVid)                
                else:            
                        try:
                                GUI.GUI()
                        except:       
                                cv2.destroyAllWindows()
                                traceback.print_exc()
                        break
                
                

            

            

