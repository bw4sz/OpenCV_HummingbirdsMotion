#Following Swinnen (2014) from:
###A Novel Method to Reduce Time Investment When Processing Videos from Camera Trap Studies###

#Import Libraries
import cv2 
import numpy as np
import argparse
import os
from shapely.ops import cascaded_union
import shapely.geometry as sg
import gc



class MotionM:
    def __init__(self,f,T,acc):
        
        ##Output location
        #file destination folder
        dest="C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/ReviewDocuments/"
        
        #make folder to hold output using the file name
        flname=os.path.splitext(os.path.basename(f))[0]
        outdr=os.path.join(dest,flname)   
        
        #make folder
        if not os.path.exists(outdr): os.mkdir(outdr)
        
        cap=cv2.VideoCapture(f)
        _,self.display_image=cap.read()
        
        #initial paramaters

        self.acc=acc
        self.threshT=T
        
        self.top = 0
        self.bottom = 1
        self.left = 0
        self.right = 1
        
        self.width = np.size(self.display_image, 1)
        self.height = np.size(self.display_image, 0)
        
        self.running_average_image = np.float32(self.display_image)
        
        
    def accAvg(self,img,towrite):

        # Use the Running Average as the static background
        cv2.accumulateWeighted(img,self.running_average_image,self.acc)        
        
        self.running_average_in_display_color_depth = cv2.convertScaleAbs(self.running_average_image)
        

        # Subtract the current frame from the moving average.
        self.difference=cv2.absdiff(img, self.running_average_in_display_color_depth)

        
        # Convert the image to greyscale.
        self.grey_image=cv2.cvtColor(self.difference,cv2.COLOR_BGR2GRAY)
        
        # Threshold the image to a black and white motion mask:
        ret,self.grey_image = cv2.threshold(self.grey_image, self.threshT, 255, cv2.THRESH_BINARY )        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        self.grey_image= cv2.morphologyEx(self.grey_image, cv2.MORPH_CLOSE, kernel)  

        
        points = []   # Was using this to hold camera_imageROIeither pixel coords or polygon coords.
        bounding_box_list = []
        
        # Now calculate movements using the white pixels as "motion" data
        _,contours,hierarchy = cv2.findContours(self.grey_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )

        if len(contours)==0:
            return(img)
        
        cnt=contours[0]
                
        drawing = np.uint8(img)
                    
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
                box_width = box[self.right][0] - box[self.left][0]
                box_height = box[self.bottom][0] - box[self.top][0]
                box_areas.append( box_width * box_height )
                
        average_box_area = 0.0
        if len(box_areas): average_box_area = float( sum(box_areas) ) / len(box_areas)
        
        trimmed_box_list = []
        for box in bounding_box_list:
                box_width = box[self.right][0] - box[self.left][0]
                box_height = box[self.bottom][0] - box[self.top][0]
                
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
                if casc.geoms[p].area > ((self.width * self.height) * (float(0.15/100))):
                        cv2.rectangle(towrite,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(255,255,0),thickness=3)
                        #Return the centroid to list, rounded two decimals
                        x=round(casc.geoms[p].centroid.coords.xy[0][0],2)
                        y=round(casc.geoms[p].centroid.coords.xy[1][0],2)
                        bound_center.append((x,y)) 
        else:
                b=casc.bounds
                #If bounding polygon is larger than the minsize, draw a rectangle
                if casc.area > ((self.width * self.height) * (float(0.15/100))):
                        cv2.rectangle(towrite,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(255,255,0),thickness=3)
                        x=round(casc.centroid.coords.xy[0][0],2)
                        y=round(casc.centroid.coords.xy[1][0],2)
                        bound_center.append((x,y))  
                        
        del self.running_average_in_display_color_depth
        del self.grey_image
        del self.difference
        del img
        
        gc.collect()        
        return(towrite)



class Static:
    def __init__(self,f,T):
        cap=cv2.VideoCapture(f)
        ret,img = cap.read()
        
        self.T=T
        cap=cv2.VideoCapture(f)
        
        ##Output location
        #file destination folder
        dest="C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/ReviewDocuments/"
        
        #make folder to hold output using the file name
        flname=os.path.splitext(os.path.basename(f))[0]
        outdr=os.path.join(dest,flname)        
        
        #make folder
        if not os.path.exists(outdr): os.mkdir(outdr)

        #empty frame
        mat=[]
        
        #Capture next frame, if there is no next frame; break.
        while (1):
            ret,img = cap.read()
            if not ret:
                break
            #resize and grayscale
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        
            mat.append(frame)        
        
        #set accumulator
        background = np.float32(mat[0]) # 32 bit accumulator
        
        for i in mat:
            cv2.accumulate(i,background)
        self.background=background/len(mat)        
            
        cv2.imwrite(os.path.join(dest,flname,"Background.jpg"), self.background)
        del mat
        gc.collect()
        
        
        #divide by number of frames
    def staticA(self,i):
        #compare the mean to each resized frame.
    
        #current frame to average
        gi = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)                
        back_depth=cv2.convertScaleAbs(self.background)
        diff=cv2.absdiff(gi,back_depth)
        ret,grey_image = cv2.threshold(diff, self.T, 255, cv2.THRESH_BINARY )
        t=grey_image.copy()
        _,contours,hierarchy = cv2.findContours(t, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE ) 
        for cnt in contours:
                bounding_rect = cv2.boundingRect( cnt )
                x,y,w,h = cv2.boundingRect(cnt)
                cv2.rectangle(i,(x,y),(x+w,y+h),(0,0,255),2)
        del t
        return(i)
    

class MOG:
    def __init__(self,f,history,vt):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=vt)
        self.history=history
        

        
    def run(self,img,towrite):
        self.grey_image = self.fgbg.apply(img)
    
        self.top = 0
        self.bottom = 1
        self.left = 0
        self.right = 1
        
        self.width = np.size(img, 1)
        self.height = np.size(img, 0)        
        
        #Dilate the areas to merge bounded objects
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        self.grey_image= cv2.morphologyEx(self.grey_image, cv2.MORPH_OPEN, kernel)
        
        points = []   # Was using this to hold camera_imageROIeither pixel coords or polygon coords.
        bounding_box_list = []
        
        # Now calculate movements using the white pixels as "motion" data
        _,contours,hierarchy = cv2.findContours(self.grey_image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )

        if len(contours)==0:
            return(img)
        
        cnt=contours[0]
                
        drawing = np.uint8(img)
                    
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
                box_width = box[self.right][0] - box[self.left][0]
                box_height = box[self.bottom][0] - box[self.top][0]
                box_areas.append( box_width * box_height )
                
        average_box_area = 0.0
        if len(box_areas): average_box_area = float( sum(box_areas) ) / len(box_areas)
        
        trimmed_box_list = []
        for box in bounding_box_list:
                box_width = box[self.right][0] - box[self.left][0]
                box_height = box[self.bottom][0] - box[self.top][0]
                
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
                if casc.geoms[p].area > ((self.width * self.height) * (float(0.1/100))):
                        cv2.rectangle(towrite,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,0),thickness=3)
                        #Return the centroid to list, rounded two decimals
                        x=round(casc.geoms[p].centroid.coords.xy[0][0],2)
                        y=round(casc.geoms[p].centroid.coords.xy[1][0],2)
                        bound_center.append((x,y)) 
        else:
                b=casc.bounds
                #If bounding polygon is larger than the minsize, draw a rectangle
                if casc.area > ((self.width * self.height) * (float(0.1/100))):
                        cv2.rectangle(towrite,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,0),thickness=3)
                        x=round(casc.centroid.coords.xy[0][0],2)
                        y=round(casc.centroid.coords.xy[1][0],2)
                        bound_center.append((x,y))          
        return(towrite)
        