import numpy as np
import cv2
from shapely.ops import cascaded_union
import shapely.geometry as sg

cap = cv2.VideoCapture('C:/Users/Ben/Desktop/MeerkatTest/garcon_test.avi')
#cap = cv2.VideoCapture('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/testing/PlotwatcherTest.TLV')

#cap=cv2.VideoCapture("F:/FieldWork2013/Santa Lucia 1/HDV_0316.mp4")

#fgbg5000 = cv2.createBackgroundSubtractorMOG2(500, 16,detectShadows = False)
fgbg1000 = cv2.createBackgroundSubtractorKNN()


for x in np.arange(0,1000):
    cap.grab()
    
def cont(orig,fram):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
    
    fr=fram.copy()
    morph=orig.copy()
    poly=orig.copy()
    
    width = np.size(fr, 1)
    height = np.size(fr, 0)
    
    # Now calculate movements using the white pixels as "motion" data
    _,contours,hierarchy = cv2.findContours(fr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
                       
    top = 0
    bottom = 1
    left = 0
    right = 1    
    
    ###Draw the initial contours
    for cnt in contours:
                bx,by,bw,bh = cv2.boundingRect(cnt)
                cv2.drawContours(fr,[cnt],0,(0,255,0),1)   # draw #contours in green color

    #morphology with contours
    morphc = cv2.morphologyEx(fram, cv2.MORPH_CLOSE, kernel)
    
    #fram = np.uint8(fram)
    # Now calculate movements using the white pixels as "motion" data
    _,contours,hierarchy = cv2.findContours(morphc, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )    
    
    for cnt in contours:
                bx,by,bw,bh = cv2.boundingRect(cnt)
                cv2.drawContours(morph,[cnt],0,(0,255,0),1)   # draw #contours in green color
    
    bounding_box_list=[]                    
    for cnt in contours:
            bounding_rect = cv2.boundingRect( cnt )
            point1 = ( bounding_rect[0], bounding_rect[1] )
            point2 = ( bounding_rect[0] + bounding_rect[2], bounding_rect[1] + bounding_rect[3] )
            bounding_box_list.append( ( point1, point2 ) )
            
    ## Find the average size of the bbox (targets), then
    ## remove any tiny bboxes (which are probably just noise).
    ## "Tiny" is defined as any box with 1/10th the area of the average box.
    ## This reduces false positives on tiny "sparkles" noise.
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
            
            ## Only keep the box if it's not a tiny noise box:
            if (box_width * box_height) > average_box_area*.3: 
                    trimmed_box_list.append( box )

    ##shapely does a much faster job of polygon union
    ##format into shapely bounding feature
    shape_list=[]
    
    ### Centroids of each target
    bound_center=[]
    
    for out in trimmed_box_list:
            sh_out=sg.box(out[0][0],out[0][1],out[1][0],out[1][1])
            shape_list.append(sh_out)

    ##shape_pol=sg.MultiPolygon(shape_list)
    casc=cascaded_union(shape_list).buffer(2)
    
    if casc.type=="MultiPolygon":
        #draw shapely bounds
        for p in range(1,len(casc.geoms)):
            b=casc.geoms[p].bounds
            if casc.geoms[p].area > ((width * height) * (float(1/100))):
                    cv2.rectangle(poly,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=2)
    else:
            b=casc.bounds
            #If bounding polygon is larger than the minsize, draw a rectangle
            if casc.area > ((width * height) * (float(1/100))):
                        cv2.rectangle(poly,(int(b[0]),int(b[1])),(int(b[2]),int(b[3])),(0,0,255),thickness=2)
    return([orig,fram,morph,poly])


def display(image,window):
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)    
    cv2.imshow(window,image)
    k = cv2.waitKey(1) & 0xff
    if k == 27: 
        print("break")        
    
while(1):
    ret, frame = cap.read()
    if not ret:
        break

    #MOG    
    #fgmask5000 = fgbg5000.apply(frame)
    #mask_rbg5000 = cv2.cvtColor(fgmask5000,cv2.COLOR_GRAY2BGR)
    #draw5000 = frame & mask_rbg5000
    
    fgmask1000 = fgbg1000.apply(frame)
    orig,fr,morph,poly = cont(orig=frame,fram=fgmask1000)

    display(orig,"orig")
    display(fr,"fr")
    display(morph,"morph")
    display(poly,"poly")
        
    #mask_rbg1000 = cv2.cvtColor(fgmask1000,cv2.COLOR_GRAY2BGR)
    #draw1000 = frame & mask_rbg1000  
    
    ##kernel opening
    #fgmaskO = cv2.morphologyEx(fgmask1000, cv2.MORPH_OPEN, kernel)
    ##cont1000=cont(fgmaskO)
     
    ##kernel closing
    #fgmaskC = cv2.morphologyEx(fgmask5000, cv2.MORPH_OPEN, kernel)
    #cont5000=cont(fgmaskC)
     

    #cv2.namedWindow('frame5000', cv2.WINDOW_NORMAL)
    #cv2.imshow('frame5000',draw5000)
    #k = cv2.waitKey(1) & 0xff
    #if k == 27:
        #break
    #cv2.namedWindow('frame1000', cv2.WINDOW_NORMAL)
    #cv2.imshow('frame1000',draw1000)
    #k = cv2.waitKey(1) & 0xff
    #if k == 27:
        #break
    #cv2.namedWindow('original', cv2.WINDOW_NORMAL)
    #cv2.imshow('original',frame)
    #k = cv2.waitKey(1) & 0xff
    #if k == 27:
        #break 
    
    #cv2.imshow('contA',cont1000)
    #k = cv2.waitKey(1) & 0xff
    #if k == 27:
        #break  
    

cap.release()
cv2.destroyAllWindows()