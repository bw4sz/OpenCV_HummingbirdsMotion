
#!/usr/bin/env python

import os

##Global variables
# BBoxes must be in the format:
# ( (topleft_x), (topleft_y) ), ( (bottomright_x), (bottomright_y) ) )
top = 0
bottom = 1
left = 0
right = 1

BLUE = (255,0,0)        # rectangle color
GREEN = (0,255,0)        # rectangle color
RED = (0,0,255)        # rectangle color


##Visualize the frames, this should only be used for testing!
vis=False

#A few hard coded testing variables, only to be used by the developers.
todraw=True
objectEdge=False

#Start time

#Set globals for mouse map, callback has unique syntax
drawing = False # true if mouse is pressed
drawing_area = False # true if mouse is pressed
roi=[]  
ix,iy = -1,-1
#Global methods

def myround(x, base=10):
    return int(base * round(float(x)/base))

def ask_acc():
        in_accAvg=raw_input("Fixed accumulated averaging (accAvg) sensitivity to motion (0.35):\n")
        if in_accAvg:
                try:
                        out=float(in_accAvg)
                        return(out)
                except Exception, e:
                        print( "Error: accAvg much be a numeric value not character." )
                        ask_acc()

def ask_file():
        in_f=raw_input("Enter video input:\n")
        if not in_f: in_f = "C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv"
        if in_f:
                if os.path.isfile(in_f): return(in_f)
                else:
                    print("File path does not exist!")
                    ask_file()
        
#define a display function
def display(window,t,image):
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.imshow(window,image)
        cv2.waitKey(t)
        cv2.destroyWindow(window)              