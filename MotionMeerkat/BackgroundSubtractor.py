####Background subtraction for Motion class
import numpy as np
import cv2
#takes in the constructor and the method chosen

class Background:
    def __init__(self,subMethod,display_image,acc,thresh):
    
        ##Subtractor Method
        self.subMethod=subMethod
        
        ####Create Background Constructor
        if self.subMethod=="Acc":
                self.grey_image = np.uint8(display_image)
                self.running_average_image = np.float32(display_image)
                self.running_average_in_display_color_depth = display_image.copy()
                self.difference =  display_image.copy()
                self.accAvg=acc
                self.threshT=thresh
    
        if self.subMethod=="MOG":
            #MOG method creator
            self.fgbg = cv2.createBackgroundSubtractorMOG2()
        if self.subMethod=="KNN":
            #MOG method creator
            self.fgbg = cv2.createBackgroundSubtractorKNN()
    
    #Frame Subtraction
    def BackGroundSub(self,camera_imageROI):
        ## accumulated averaging
        if self.subMethod == "Acc":
            # Create an image with interactive feedback:
            self.display_image = camera_imageROI.copy()
            
            # Create a working "color image" to modify / blur
            self.color_image =  self.display_image.copy()
            
            #if vis: display(Initial,2000,color_image)                    
        
            # Smooth to get rid of false positives
            self.color_image = cv2.GaussianBlur(self.color_image,(3,3),0)
                       
            # Use the Running Average as the static background
            cv2.accumulateWeighted(self.color_image,self.running_average_image,self.accAvg)                                  
            self.running_average_in_display_color_depth = cv2.convertScaleAbs(self.running_average_image)
                                       
            # Subtract the current frame from the moving average.
            self.difference=cv2.absdiff( self.color_image, self.running_average_in_display_color_depth)
            
            #if vis: display("difference",5000,difference)
            
            # Convert the image to greyscale.
            self.grey_image=cv2.cvtColor( self.difference,cv2.COLOR_BGR2GRAY)
            
            # Threshold the image to a black and white motion mask:
            ret,self.grey_image = cv2.threshold(self.grey_image, self.threshT, 255, cv2.THRESH_BINARY )
        
        #display("Before closing",1500,grey_image)
        
        ##Mixture of Gaussians
        if self.subMethod in ["MOG","KNN"]:
            self.grey_image = self.fgbg.apply(camera_imageROI)
        
        #Dilate the areas to merge bounded objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
        self.grey_image= cv2.morphologyEx(self.grey_image, cv2.MORPH_OPEN, kernel)
        return(self.grey_image)