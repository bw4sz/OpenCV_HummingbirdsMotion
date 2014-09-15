#!/usr/bin/env python
from sourceM import *
from motionClass import *

#==================
# MAIN ENTRY POINT
#==================

if __name__ == "__main__":
        while True:
                try:
                        motionVid=Motion()
                        motionVid.arguments()
                        motionVid.wrap()
                except:
                        traceback.print_exc()
        
                #reboot or exit?
                #if there were system arguments, immediately exit
                if len(sys.argv)>=2:
                        break
                ch=raw_input("Press r to reboot, press any key to exit \n")
                if ch=='r':
                        continue
                break
            


