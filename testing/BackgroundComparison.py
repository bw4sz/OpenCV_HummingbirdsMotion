import numpy as np
import cv2

#cap = cv2.VideoCapture('C:/Users/Ben/Desktop/MeerkatTest/garcon_test.avi')
cap = cv2.VideoCapture('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/testing/PlotwatcherTest.TLV')

#fgbgMOG2 = cv2.createBackgroundSubtractorMOG2(detectShadows = False)
fgbgKNN = cv2.createBackgroundSubtractorKNN(detectShadows=False)

while(1):
    ret, frame = cap.read()
    if not ret:
        break

    #MOG    
    #fgmask = fgbgMOG2.apply(frame)
    #KNN
    fgmaskKNN = fgbgKNN.apply(frame)
    
    #accumulated averaging
    # Create an image with interactive feedback:
    #display_image = frame.copy()
    
    ## Create a working "color image" to modify / blur
    #color_image =  display_image.copy()\
    
    ## Smooth to get rid of false positives
    #color_image = cv2.GaussianBlur(color_image,(3,3),0)
        
    ## Use the Running Average as the static background
    #running_average_image = np.float32(display_image)
    
    #cv2.accumulateWeighted(color_image,running_average_image,.1)                                  
    #running_average_in_display_color_depth = cv2.convertScaleAbs( running_average_image)
                        
    ## Subtract the current frame from the moving average.
    #difference=cv2.absdiff( color_image, running_average_in_display_color_depth)
        
    ## Convert the image to greyscale.
    #grey_image=cv2.cvtColor( difference,cv2.COLOR_BGR2GRAY)

    ## Threshold the image to a black and white motion mask:
    #ret,grey_image = cv2.threshold(grey_image, 5, 255, cv2.THRESH_BINARY )

    #cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    #cv2.imshow('frame',fgmask)
    #k = cv2.waitKey(5) & 0xff
    #if k == 27:
        #break
    
    #cv2.namedWindow('frameKNN', cv2.WINDOW_NORMAL)    
    #cv2.imshow('frameKNN',fgmaskKNN)
    #k = cv2.waitKey(5) & 0xff
    #if k == 27:
        #break
    
    #cv2.namedWindow('acc', cv2.WINDOW_NORMAL)    
    #cv2.imshow('acc',grey_image)
    #k = cv2.waitKey(5) & 0xff
    #if k == 27:
        #break    
    

cap.release()
cv2.destroyAllWindows()