#From http://blog.christianperone.com/2015/01/real-time-drone-object-tracking-using-python-and-opencv/

import numpy as np
import cv2
import sourceM
import BackgroundSubtractor

def run_main():
    cap = cv2.VideoCapture('C:/Users/Ben/Downloads/test.avi')
    #cap= cv2.VideoCapture("C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/PlotwatcherTest.tlv")
    # Read the first frame of the video
    ret, frame = cap.read()
    # Set the ROI (Region of Interest).
    select=sourceM.Urect(frame.copy(),"Set ROI")
    
    #turn to x y width and height
    xi,yi,hi,wi=(select[0],select[1],abs(select[1]-select[3]),abs(select[0]-select[2]))
    
    #xi,yi,wi,hi = 275,220,80,60
    track_window=(xi,yi,wi,hi)
        
    #crop frame
    roi = frame[yi:yi+hi, xi:xi+wi]
            
    # Create mask and normalized histogram
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((255.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1)
    
    #Create background subtractor
    #full=BackgroundSubtractor.Background("Acc",frame,0.35,10,100,16)
    #crop=BackgroundSubtractor.Background("Acc",roi,0.35,10,100,16)
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0,180], 1)
        
        ret, track_window = cv2.meanShift(dst, track_window, term_crit)
        x,y,w,h = track_window
        
        toshow=frame.copy()
        cv2.rectangle(toshow, (xi,yi), (xi+wi,yi+hi), 0, 3)
        cv2.rectangle(toshow, (x,y), (x+w,y+h), 255, 1)
        
        cv2.putText(toshow, 'Tracked', (x-25,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
        #plot original
        cv2.imshow('Tracking', toshow)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        
        #get subframe
        #subframe = frame[x:x+h, y:y+w]

        #Apply background subtraction
        #grey_full=full.BackGroundSub(frame)
        #grey_crop=crop.BackGroundSub(subframe)

        
    cap.release()
    

    cv2.destroyAllWindows()
if __name__ == "__main__":
    run_main()