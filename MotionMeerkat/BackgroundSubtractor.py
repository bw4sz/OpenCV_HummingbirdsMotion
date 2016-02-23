####Background subtraction for Motion class
import numpy as np
import cv2
import sourceM

#takes in the constructor and the method chosen

class Background:
    def __init__(self,subMethod,display_image,acc,thresh,mogvariance):
    
        ##Subtractor Method
        self.subMethod=subMethod
        
        ####Create Background Constructor
        if self.subMethod in ["Acc","Both"]:
                self.running_average_image = np.float32(display_image)
                self.accAvg=acc
                self.threshT=thresh
    
        if self.subMethod in ["MOG","Both"]:
            #MOG method creator
            self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
            self.fgbg.setBackgroundRatio(0.95)
    
    #Frame Subtraction
    def BackGroundSub(self,camera_imageROI,learningRate):
        ## accumulated averaging
        if self.subMethod in ["Acc","Both"]:
            # Create an image with interactive feedback:
            self.display_image = camera_imageROI.copy()
            
            # Create a working "color image" to modify / blur
            self.color_image =  self.display_image.copy()
                    
            # Smooth to get rid of false positives
            self.color_image = cv2.GaussianBlur(self.color_image,(3,3),0)
                       
            # Use the Running Average as the static background
            cv2.accumulateWeighted(self.color_image,self.running_average_image,self.accAvg)                                  
            self.running_average_in_display_color_depth = cv2.convertScaleAbs(self.running_average_image)
            
            #Needs to be manually commented if vis
            #sourceM.displayV("Background image",10,self.running_average_in_display_color_depth)
            
            # Subtract the current frame from the moving average.
            self.difference=cv2.absdiff( self.color_image, self.running_average_in_display_color_depth)
                        
            # Convert the image to greyscale.
            self.grey_image=cv2.cvtColor( self.difference,cv2.COLOR_BGR2GRAY)

            #Capture the average threshold of the image
            #self.avg_threshold.append(self.grey_image.mean())
            
            # Threshold the image to a black and white motion mask:
            ret,self.grey_image = cv2.threshold(self.grey_image, self.threshT, 255, cv2.THRESH_BINARY )
                
        ##Mixture of Gaussians
        if self.subMethod in ["MOG","KNN","Both"]:
            self.grey_image = self.fgbg.apply(camera_imageROI,learningRate=learningRate)
            
            #if vis
            #bgimage=self.fgbg.getBackgroundImage()
            #cv2.imshow("Background",bgimage)
            #cv2.waitKey(1)
            
        #Erode to remove noise, dilate the areas to merge bounded objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
        self.grey_image= cv2.morphologyEx(self.grey_image, cv2.MORPH_OPEN, kernel)
        return(self.grey_image)
    