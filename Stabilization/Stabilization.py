import cv2
import numpy
import ctypes
import random
import kdtree

#Adapted from http://opticks.org/confluence/display/opticksExtras/Using+animation+callbacks+to+stabilize+video

#will need to recompile 
##The calc_pts() function uses the SURF algorithm to extracts good points in the image to track. These are likely to be strong and distinguishable in future frames. See the SURF website for more information on the algorithm. The ExtractSURF() function returns much more data than we need for this example so we throw out everything except the (x,y) coordinates at the center of the features.
def calc_pts(d):
    tmp = cv2.SURF.detect(d, None, cv.CreateMemStorage(), (0, 3000, 3, 1))
    return map(lambda x: x[0], tmp[0])

def calc_initial(a, b):
    out = []
    for pt in b: out.append((a.query(pt, t=1)[0], pt))
    return out


#Second idea
