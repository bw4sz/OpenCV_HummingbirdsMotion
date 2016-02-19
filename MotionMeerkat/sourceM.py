
#!/usr/bin/env python

import os
import cv2

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

#Set globals for mouse map, callback has unique syntax
drawing = False # true if mouse is pressed
drawing_area = False # true if mouse is pressed
roi=[]  
ix,iy = -1,-1

##Visualize the frames, this should only be used for testing!
vis=False

#A few hard coded testing variables, only to be used by the developers.
todraw=True
objectEdge=False

#Start time


#Global methods

def myround(x, base=10):
    return int(base * round(float(x)/base))

def ask_acc():
        in_accAvg=raw_input("Accumulated averaging sensitivity to motion (0.35)\n0.1 would be very sensitive to movement,\n0.5 would be fairly insensitive to movement:\n")
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

#define a video diplay function
def displayV(window,t,image):
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.imshow(window,image)
        cv2.waitKey(t)
        
#define a sorting function
def getint(name):
        f=os.path.split(name)
        (shortname, extension) = os.path.splitext(f[-1]) 
        return int(shortname)
    
##User drawn rectangles

def Urect(img,title):
    def onmouse(event,x,y,flags,param):
        global ix,iy,roi,drawing        
        
        # Draw Rectangle
        if event == cv2.EVENT_RBUTTONDOWN:
            drawing = True
            ix,iy = x,y

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                cv2.rectangle(img,(ix,iy),(x,y),BLUE,-1)
                rect = (ix,iy,abs(ix-x),abs(iy-y))

        elif event == cv2.EVENT_RBUTTONUP:
            drawing = False
            cv2.rectangle(img,(ix,iy),(x,y),BLUE,-1)
            rect = (ix,iy,x,y)
            roi.extend(rect)

    cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(title,onmouse)

    print ("Right click and hold to draw a single rectangle ROI, beginning at the top left corner of the desired area. A blue box should appear. Hit esc to exit screen.")
    while(1):
            cv2.namedWindow(title,cv2.WINDOW_NORMAL)                 
            cv2.imshow(title,img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                    break
    
    cv2.destroyAllWindows()
    
    return(roi)    

    
def adaptF():
        #Every 10min, reset the accAvg threshold, depending on expected level of movement
    
        #Should be a integer, round it
        fift=round(10*60*float(self.frame_rate))
        
        if self.frame_count % fift == 0:  
                
               #If the total base is fift (10min window), then assuming 99% of images are junk the threshold should be
                #We've been counting frames output to file in the hitcounter
                
                print(str(self.hitcounter) + " files written in last 10minutes" + "\n" )             
                if self.hitcounter > (fift*self.frameHIT) :
                        self.accAvg = self.accAvg + .05
                if self.hitcounter < (fift*self.frameHIT) :
                        self.accAvg = self.accAvg - .025
                        
                #In my experience its much more important to drop the sensitivity, than to increase it, so i've make the adapt filter move downwards slower than upwards. 
                print(self.file_destination + str(self.frame_count) + " accAvg is changed to: " + str(self.accAvg) + "\n")
                
                #Write change to log file
                
                #reset hitcoutner for another fifteen minutes
                self.hitcounter=0
                                                                
                #Build in a floor, the value can't be negative.
                if self.accAvg < self.floorvalue:
                        self.floor=self.floor + 1
                
        #Reset if needed.
                if self.floor == 1 :
                        self.accAvg=self.floorvalue
    
                        print(self.file_destination + str(self.frame_count) + " accAvg is reset to: " + str(self.accAvg))
                        #Write change to log file    
                        
        #return new accAvg setting
        return(self.accAvg)
    