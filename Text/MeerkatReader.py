#Text reader
import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
from pylab import *
import sourceM

ioff()

files=glob.glob("C:/Users/Ben\Dropbox/Thesis/Maquipucuna_SantaLucia/HolgerCameras/201608/*")

print files[0]

img=cv2.imread(files[0])

#Set region of interest 
roi_selected=sourceM.Urect(img.copy(),"Region of Interest")
roi_selected=roi_selected[-4:]
if len(roi_selected)==0 :
    raise ValueError('Error: No box selected. Please select an area by right clicking and dragging with your cursor to create a box. Hit esc to exit the window.')
display_image=img[roi_selected[1]:roi_selected[3], roi_selected[0]:roi_selected[2]]
     
display_image=cv2.cvtColor(display_image,cv2.COLOR_RGB2GRAY)

#resize
display_image = cv2.resize(display_image,None,fx=20, fy=20, interpolation = cv2.INTER_LINEAR)

fig = plt.figure()
plt.imshow(display_image,cmap="gray")
fig = plt.show()        

#threshold
ret,display_image=cv2.threshold(display_image,240,255,cv2.THRESH_BINARY)

#opening
kernel = np.ones((20,20),np.uint8)
display_image=cv2.morphologyEx(display_image,cv2.MORPH_CLOSE,kernel)

display_image = cv2.bitwise_not(display_image)

fig = plt.figure()
plt.imshow(display_image,cmap="gray")
fig = plt.show()        

#inverse
display_image = cv2.bitwise_not(display_image)

##Try tesseract
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract

img = Image.fromarray(display_image)
i = pytesseract.image_to_string(img,lang="eng")
print i


