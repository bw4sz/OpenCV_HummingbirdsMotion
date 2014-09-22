####Background subtraction for Motion class
import numpy as np
import cv2
#takes in the constructor and the method chosen

class Background:
    def __init__(self,subMethod,display_image,acc,thresh,moghistory):
    
        ##Subtractor Method
        self.subMethod=subMethod
        
        ####Create Background Constructor
        if self.subMethod=="Acc":
                self.running_average_image = np.float32(display_image)
                self.accAvg=acc
                self.threshT=thresh
    
        if self.subMethod=="MOG":
            #MOG method creator
            self.fgbg = cv2.createBackgroundSubtractorMOG2(history=moghistory, detectShadows=False)
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
                
        ##Mixture of Gaussians
        if self.subMethod in ["MOG","KNN"]:
            self.grey_image = self.fgbg.apply(camera_imageROI)
        
        #Dilate the areas to merge bounded objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
        self.grey_image= cv2.morphologyEx(self.grey_image, cv2.MORPH_OPEN, kernel)
        return(self.grey_image)
    
    def contourFilter(grey_image,minSize,ROI_include):
        
        global display_image, camera_imageO
        
        points = []   # Was using this to hold either pixel coords or polygon coords.
        bounding_box_list = []

        # Now calculate movements using the white pixels as "motion" data
        _,contours,hierarchy = cv2.findContours(grey_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
        
        if len(contours) == 0 :
                #No movement, add to counter
                self.nocountr=self.nocountr+1
                #NoMotion flag
                noMotion=True
                return("Empty")
        
        cnt=contours[0]
        len(cnt)
                
        drawing = np.uint8(display_image)
        
        for cnt in contours:
                bounding_rect = cv2.boundingRect( cnt )
                point1 = ( bounding_rect[0], bounding_rect[1] )
                point2 = ( bounding_rect[0] + bounding_rect[2], bounding_rect[1] + bounding_rect[3] )
                bounding_box_list.append( ( point1, point2 ) )
                
                
        # Find the average size of the bbox (targets), then
        # remove any tiny bboxes (which are probably just noise).
        # "Tiny" is defined as any box with 1/10th the area of the average box.
        # This reduces false positives on tiny "sparkles" noise.
        box_areas = []
        for box in bounding_box_list:
                box_width = box[right][0] - box[left][0]
                box_height = box[bottom][0] - box[top][0]
                box_areas.append( box_width * box_height )
                
        average_box_area = 0.0
        if len(box_areas): average_box_area = float( sum(box_areas) ) / len(box_areas)
        
        trimmed_box_list = []
        for box in bounding_box_list:
                box_width = box[right][0] - box[left][0]
                box_height = box[bottom][0] - box[top][0]
                
                # Only keep the box if it's not a tiny noise box:
                if (box_width * box_height) > average_box_area*.3: 
                        trimmed_box_list.append( box )

        #shapely does a much faster job of polygon union
        #format into shapely bounding feature
        shape_list=[]
        
        ## Centroids of each target
        bound_center=[]
        
        for out in trimmed_box_list:
                sh_out=sg.box(out[0][0],out[0][1],out[1][0],out[1][1])
                shape_list.append(sh_out)

        #shape_pol=sg.MultiPolygon(shape_list)
        casc=cascaded_union(shape_list).buffer(1)
        
        if casc.type=="MultiPolygon":
            #draw shapely bounds
            for p in range(1,len(casc.geoms)):
                b=casc.geoms[p].bounds
                if casc.geoms[p].area > ((width * height) * (float(minSIZE/100))):
                        if ROI_include == "exclude":
                                cv2.rectangle(camera_imageO,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=2)
                                #cv2.putText(camera_imageO, str(round(casc.geoms[p].area/(width * height),3)*100), (int(b[0]),int(b[1])),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),1,-1)
            
                        else:
                                cv2.rectangle(display_image,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=2)
                        #Return the centroid to list, rounded two decimals
                        x=round(casc.geoms[p].centroid.coords.xy[0][0],2)
                        y=round(casc.geoms[p].centroid.coords.xy[1][0],2)
                        bound_center.append((x,y)) 
        else:
                b=casc.bounds
                #If bounding polygon is larger than the minsize, draw a rectangle
                if casc.area > ((width * height) * (float(minSIZE/100))):
                        if ROI_include == "exclude":
                                cv2.rectangle(camera_imageO,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=2)
                                #cv2.putText(camera_imageO, str(round(casc.area/(width * height),3)*100),(int(b[0]),int(b[1])),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1,-1)
                        else:
                                cv2.rectangle(display_image,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=2)
                        x=round(casc.centroid.coords.xy[0][0],2)
                        y=round(casc.centroid.coords.xy[1][0],2)
                        bound_center.append((x,y)) 
                        
                        #return bounding boxes and centers
                        
        