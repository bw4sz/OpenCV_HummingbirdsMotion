#!/usr/bin/env python

import motionClass
import wrapper
import arguments
import traceback
import sys
import numpy as np
import numpy.core.multiarray
import ctypes
import shapely
import cv2
import FileDialog
import GUI

#==================
# MAIN ENTRY POINT
#==================

#Define ending function
def ending():
    while True:
        ch=raw_input("Enter r to reboot, Enter x to exit \n")
        if ch=='r':
            return(ch)
        if ch=='x':
            return(ch)

if __name__ == "__main__":
        while True:
            try:
                GUI.GUI()
            except:       
                cv2.destroyAllWindows()
                traceback.print_exc()
                ch=ending()
                if ch == 'r': continue
                if ch == 'x': break 
                
                

            

            

