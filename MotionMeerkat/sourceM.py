
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
        
#define a sorting function
def getint(name):
        f=os.path.split(name)
        (shortname, extension) = os.path.splitext(f[-1]) 
        return int(shortname)
    
##User drawn rectangles

def Urect(img,title):
    #make a copy of the image.
    roi=[]

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

    cv2.namedWindow(title,cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(title,onmouse)

    print ("Please draw a single rectangle ROI using right click!")
    while(1):
            cv2.namedWindow(title,cv2.WINDOW_AUTOSIZE)                 
            cv2.imshow(title,img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                    break
    
    cv2.destroyAllWindows()
    
    return(roi)    


def adapt(frame_rate=self.frame_rate,accAvg=self.accAvg,file_destination=file_destination,floorvalue=self.floorvalue):
    #Every 10min, reset the accAvg threshold, depending on expected level of movement

    #Should be a integer, round it
    fift=round(10*60*float(frame_rate))
    
    if frame_count % fift == 0:  
            
           #If the total base is fift (10min window), then assuming 99% of images are junk the threshold should be
            #We've been counting frames output to file in the hitcounter
            
            print(str(hitcounter) + " files written in last 10minutes" + "\n" )             
            if hitcounter > (fift*frameHIT) :
                    accAvg = accAvg + .05
            if hitcounter < (fift*frameHIT) :
                    accAvg = accAvg - .025
                    
            #In my experience its much more important to drop the sensitivity, than to increase it, so i've make the adapt filter move downwards slower than upwards. 
            print(file_destination + str(frame_count) + " accAvg is changed to: " + str(accAvg) + "\n")
            
            #Write change to log file
            
            #reset hitcoutner for another fifteen minutes
            hitcounter=0
                                                            
            #Build in a floor, the value can't be negative.
            if accAvg < floorvalue:
                    floor=floor + 1
            
    #Reset if needed.
            if floor == 1 :
                    accAvg=floorvalue

                    print(file_destination + str(frame_count) + " accAvg is reset to: " + str(self.accAvg))
                    #Write change to log file    
                    
    #return new accAvg setting
    return(accAvg)