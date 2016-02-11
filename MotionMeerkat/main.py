#!/usr/bin/env python
import motionClass
import wrapper
import arguments
import traceback
import sys
import numpy
import numpy.core.multiarray



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
                    motionVid=motionClass.Motion()
                    arguments.arguments(motionVid)
                    wrapper.wrap(motionVid)
                    
            except ValueError, e:
                    if e.message!= 'Failed to load OpenC runtime':
                            raise ValueError, e
    
            #reboot or exit?
            #if there were system arguments, immediately exit
            if len(sys.argv)>=2:
                    break
            ch=ending()
            if ch == 'r': continue
            if ch == 'x': break

            

