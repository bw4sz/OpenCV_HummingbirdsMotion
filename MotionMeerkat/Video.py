import cv2
import sys
if sys.version_info >= (3, 0):
    from urllib import urlparse
else:
    from urlparse import urlparse
import math
from datetime import datetime, timedelta
import os
import numpy as np
from Geometry import *
import csv
import time
import Crop
import libbgs

#general functions
def get_spaced_colors(n):
    max_value = 16581375 #255**3
    interval = int(max_value / n)
    colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]
    
    return [(int(i[:2], 16), int(i[2:4], 16), int(i[4:], 16)) for i in colors]

def mult(p,x):
    return(int(p+p*x))

def check_bounds(img,axis,p):
    if p > img.shape[axis]:
        p=img.shape[axis]
    if p < 0:
        p=0
    return(p)

def resize_box(img,bbox,m=math.sqrt(2)-1):

    #expand box by multiplier m, limit to image edge

    #max height
    p1=mult(bbox.y+bbox.h,-m)
    p1=check_bounds(img, 0, p1)

    #min height
    p2=mult(bbox.y,m)            
    p2=check_bounds(img, 0, p2)            

    #min width
    p3=mult(bbox.x,-m)            
    p3=check_bounds(img, 1, p3)            

    #max width
    p4=mult(bbox.x+bbox.w,m)                        
    p4=check_bounds(img, 1, p4)            

    #create a mask, in case its bigger than image            
    cropped_image=img[p1:p2,p3:p4]

    #Resize Image
    resized_image = cv2.resize(cropped_image, (299, 299))  
    return(resized_image)

#Background subtraction functions
#Frame Subtraction
def background_apply(bgmodel,original_image):

    #Apply Subtraction
    image = bgmodel.apply(original_image)

    #Erode to remove noise, dilate the areas to merge bounded objects
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
    image=cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    return image

def find_contour(foreground):
    _,contours,hierarchy = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    contours = [contour for contour in contours if cv2.contourArea(contour) > 50]
    return contours


    
class Video:
    def __init__(self,vid,args):
                
        #start time
        self.start_time=time.time()
        
        #store args from MotionMeerkat
        self.args=args
        self.args.video=vid
        
        #set descriptors
        self.frame_count=0
        
        #Annotations dictionary
        self.annotations={}
        
        #create output directory
        #if google cloud storage file
        if self.args.input[0:3] =="gs:":
            self.googlecloud=True
            
            credentials = GoogleCredentials.get_application_default()
            storage_client = storage.Client()
            self.parsed = urlparse(args.input_dir)
        
            #parse gcp path
            self.bucket = storage_client.get_bucket(self.parsed.hostname)    
            
            #Write to temp then send to google cloud
            handle, self.file_destination = tempfile.mkdtemp()
                            
        else:
            self.googlecloud=False
            
            normFP=os.path.normpath(self.args.input)
            (filepath, filename)=os.path.split(normFP)
            (shortname, extension) = os.path.splitext(filename)
            (_,IDFL) = os.path.split(filepath) 
            
            if self.args.batch:
                self.file_destination=os.path.join(self.args.output,shortname)        
            else:
                self.file_destination=os.path.join(self.args.output,IDFL)
                self.file_destination=os.path.join(self.file_destination,shortname)        
    
            if not os.path.exists(self.file_destination):
                os.makedirs(self.file_destination)        
            
        #read video
        self.cap=cv2.VideoCapture(self.args.video)
        
        #set frame frate
        self.frame_rate=round(self.cap.get(5))
        
        #This seems to misinterpret just .tlv files
        if extension in ['.tlv','.TLV']: 
            self.frame_rate=1
            print("File type is .tlv, setting frame rate to 1 fps")        

        #background subtraction
        self.background_models=self.create_background() 
        
        #Detector almost always returns first frame
        self.IS_FIRST_FRAME = True
        
        #colors
        self.colors=get_spaced_colors(len(self.background_models))
                       
    def analyze(self):
         
        if self.args.show: 
            cv2.namedWindow("Motion_Event")
            #cv2.namedWindow("Background")            
            
        while True:
            
            #show frame counter
            Motion=False
            
            #read frame
            ret,self.original_image=self.read_frame()
            
            if not ret:
                #end time
                self.end_time=time.time()
                break
            
            self.frame_count+=1
            
            #adapt settings of mogvariance to keep from running away
            #self.adapt()
            
            for index,bg in enumerate(self.background_models):
                
                #background subtraction
                foreground=background_apply(bg,self.original_image)
                
                #view the background
                #bg=self.fgbg.getBackgroundModel()
                #cv2.imshow("Background", bg)
                #cv2.waitKey(10)            
                
                #skip the first frame after adding it to the background.
                if self.IS_FIRST_FRAME:
                    #minimum box size
                    width = np.size(self.original_image, 1)
                    height = np.size(self.original_image, 0)
                    self.original_area = width * height                    
                    print("Skipping first frame")
                    self.IS_FIRST_FRAME=False
                    continue
                
                #contour analysis
                contours=find_contour(foreground)
                
                #Next frame if no contours
                if len(contours)==0:
                    continue
                  
                #bounding boxes
                bounding_boxes = self.cluster_bounding_boxes(contours)
                
                #Next frame if no bounding boxes
                if len(bounding_boxes)==0:
                    continue
                    
                #remove if smaller than min size                
                remaining_bounding_box=[]
                for bounding_box in bounding_boxes:
                    if self.original_area * self.args.size < bounding_box.h * bounding_box.w:
                        remaining_bounding_box.append(bounding_box)
                
                #next frame is no remaining bounding boxes
                if len(remaining_bounding_box)==0:
                    continue
                
                self.annotations[self.frame_count] = remaining_bounding_box
                
                Motion=True
                if self.args.todraw:                     
                    for bounding_box in remaining_bounding_box:
                        cv2.rectangle(self.original_image, (bounding_box.x, bounding_box.y), (bounding_box.x+bounding_box.w, bounding_box.y+bounding_box.h), self.colors[index], 2)
            if self.args.show:
                if Motion:
                    cv2.imshow("Motion_Event", self.original_image)
                    cv2.waitKey(1000)
        cv2.destroyAllWindows()            
        
    #Create background objects based on input args        
    def create_background(self):    
        bgmodels=[]
        bgmodels.append(cv2.createBackgroundSubtractorMOG2(detectShadows=False,varThreshold=float(self.args.mogvariance)))
        #self.fgbg.setBackgroundRatio(0.95)
        
        #bgmodels.append(libbgs.SuBSENSE())
        return bgmodels
        
    def read_frame(self):
        
        #read frame
        ret,image=self.cap.read()
        
        if not ret:
            return((ret,image))
        
        #set crop settings if first frame
        if self.IS_FIRST_FRAME:
            if self.args.crop:
                self.roi=Crop.Crop(image,"Crop")            
        if self.args.crop:
            cropped_image=image[self.roi[1]:self.roi[3], self.roi[0]:self.roi[2]]
            return((ret,cropped_image))
        else:
            return((ret,image))    
    
    def cluster_bounding_boxes(self, contours):
        bounding_boxes = []
        for i in range(len(contours)):
            x1,y1,w1,h1 = cv2.boundingRect(contours[i])

            parent_bounding_box = self.get_parent_bounding_box(bounding_boxes, i)
            if parent_bounding_box is None:
                parent_bounding_box = self.BoundingBox(Rect(x1, y1, w1, h1))
                parent_bounding_box.members.append(i)
                bounding_boxes.append(parent_bounding_box)

            for j in range(i+1, len(contours)):
                if self.get_parent_bounding_box(bounding_boxes, j) is None:
                    x2,y2,w2,h2 = cv2.boundingRect(contours[j])
                    rect = Rect(x2, y2, w2, h2)
                    distance = parent_bounding_box.rect.distance_to_rect(rect)
                    if distance < 50:
                        parent_bounding_box.update_rect(self.extend_rectangle(parent_bounding_box.rect, rect))
                        parent_bounding_box.members.append(j)
        return bounding_boxes
    def get_parent_bounding_box(self, bounding_boxes, index):
        for bounding_box in bounding_boxes:
            if index in bounding_box.members:
                return bounding_box
        return None

    def extend_rectangle(self, rect1, rect2):
        x = min(rect1.l_top.x, rect2.l_top.x)
        y = min(rect1.l_top.y, rect2.l_top.y)
        w = max(rect1.r_top.x, rect2.r_top.x) - x
        h = max(rect1.r_bot.y, rect2.r_bot.y) - y
        return Rect(x, y, w, h)    
    
    class BoundingBox:
        def update_rect(self, rect):
            self.rect = rect
            self.x = rect.l_top.x
            self.y = rect.l_top.y
            self.w = rect.width
            self.h = rect.height
            self.time=None

        def __init__(self, rect):
            self.update_rect(rect)
            self.members = []    
    
    def write(self):      
        
        #write parameter logs        
        self.output_args=self.file_destination + "/parameters.csv"
        with open(self.output_args, 'wb') as f:  
            writer = csv.writer(f,)
            writer.writerows(self.args.__dict__.items())
            
            #Total time
            self.total_min=round((self.end_time-self.start_time)/60,3)
            writer.writerow(["Minutes",self.total_min])
            
            #Frames in file
            writer.writerow(["Total Frames",self.frame_count])
            
            #Frames returned to file
            writer.writerow(["Motion Events",len(self.annotations)])
            
            #Hit rate
            len(self.annotations)
            writer.writerow(["Return rate",float(len(self.annotations)/self.frame_count)])
            
            #Frames per second
            writer.writerow(["Frame processing rate",round(float(self.frame_count)/(self.total_min*60),2)])
        
        #Write frame annotations
        self.output_annotations=self.file_destination + "/annotations.csv"
        with open(self.output_annotations, 'wb') as f:  
            writer = csv.writer(f,)
            writer.writerow(["Frame","x","y","h","w"])
            for x in self.annotations.keys():   
                bboxes=self.annotations[x]
                for bbox in bboxes: 
                    writer.writerow([x,bbox.x,bbox.y,bbox.h,bbox.w])
                    
        if self.googlecloud:
            #write bounding boxes to google cloud
            
            blob=self.bucket.blob(self.parsed.path[1:]+"/annotations.csv")
            blob.upload_from_filename(self.output_annotations)            

            #write parameter log to google cloud
            blob=self.bucket.blob(self.parsed.path[1:]+"/parameters.csv")
            blob.upload_from_filename(self.output_args)            
            
                    
    def adapt(self):
        
            #If current frame is a multiple of the 1000 frames
            if self.frame_count % 1000 == 0:                                  
                #get the percent of frames returned in the last 10 minutes
                if (sum([x < self.frame_count-1000 for x in self.annotations.keys()])/1000) > 0.05:
                        
                    #increase tolerance rate
                    self.args.mogvariance+=5
    
                    #add a ceiling
                    if self.args.mogvariance > 120: 
                        self.args.mogvariance = 120
                    print("Adapting to video conditions: increasing MOG variance tolerance to %d" % self.args.mogvariance)
        
            
            
            