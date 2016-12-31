#Text reader
import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
from pylab import *
import sourceM
from imutils import contours

ion()

files=glob.glob("C:/Users/Ben\Dropbox/Thesis/Maquipucuna_SantaLucia/HolgerCameras/201608/*")

print files[0]

img=cv2.imread(files[0])

#Set region of interest 
roi_selected=sourceM.Urect(img.copy(),"Region of Interest")
roi_selected=roi_selected[-4:]
if len(roi_selected)==0 :
    raise ValueError('Error: No box selected. Please select an area by right clicking and dragging qwith your cursor to create a box. Hit esc to exit the window.')

fig = plt.figure()

#loop through images
#for x in files:

IDlist=[]
for f in files[0:2]:   
    img=cv2.imread(f)
    display_image=img[roi_selected[1]:roi_selected[3], roi_selected[0]:roi_selected[2]]     
    display_image=cv2.cvtColor(display_image,cv2.COLOR_RGB2GRAY)
    
    plt.imshow(display_image,cmap="Greys")    
    fig = plt.show()        
    plt.pause(0.00001)

    #resize
    display_image = cv2.resize(display_image,None,fx=10, fy=10, interpolation = cv2.INTER_CUBIC)
    
    plt.imshow(display_image,cmap="Greys")
    fig = plt.show()        
    plt.pause(0.00001)

    #threshold
    ret,display_image=cv2.threshold(display_image,247,255,cv2.THRESH_BINARY)
    
    plt.imshow(display_image,cmap="Greys")
    fig = plt.show()        
    plt.pause(0.00001)
    
    #smoth
    display_image=cv2.GaussianBlur(display_image,(5,5),0)
    
    #Closing
    kernel = np.ones((20,20),np.uint8)
    display_image=cv2.morphologyEx(display_image,cv2.MORPH_CLOSE,kernel)
    
    plt.imshow(display_image,cmap="Greys")
    fig = plt.show()        
    plt.pause(0.00001)
    
    ##split into letters##
    #get contours
    draw=display_image.copy()
    
    _,cnts,hierarchy = cv2.findContours(display_image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    len(cnts)
    
    for x in cnts:
        cv2.drawContours(draw,[x],-1,(100,100,255),3)
    plt.imshow(draw,cmap="Greys")
    fig = plt.show()        
    plt.pause(0.00001)

    #get rid of child
    #order contour left to right
    (cnts, _) = contours.sort_contours(cnts)    
    
    #remove tiny contours
    contsize = []
    for x in cnts:
        area=cv2.contourArea(x)
        if area > 1000:
            contsize.append(x)
        else:
            print str(area) + " is removed"
    
    #bouding boxes
    bounding_box_list=[]
    for cnt in contsize:
        cbox = cv2.boundingRect( cnt )
        bounding_box_list.append( cbox )
    
    #boxes as seperate matrices, make slightly larger so edges don't touch
    ID=[]
    for bbox in bounding_box_list:
        
        letter=display_image[bbox[1]-10:bbox[1]+bbox[3]+10,bbox[0]-10:bbox[0]+bbox[2]+10]
        #inverse
        letter = cv2.bitwise_not(letter)    
        
        if letter is None:
            break
        plt.imshow(letter,cmap="gray")
        fig = plt.show()        
        plt.pause(0.00001)
        
        ##Try tesseract
        try:
            import Image
        except ImportError:
            from PIL import Image
        import pytesseract
        
        img = Image.fromarray(letter)
        i = pytesseract.image_to_string(img,lang="eng",config="-psm 10")
        ID.append(i)
    print "ID is:" + str(ID)
    IDlist.append(ID)
#make known errors
#there are no =
