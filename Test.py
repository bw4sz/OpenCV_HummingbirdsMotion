import cv2
import numpy

photo = 'C:/Users/Ben/Dropbox/Posters_Presentations/PredObs_AMNH/Images/Gorgeted-Sunangel-tbl_4172'


# Load an color image in grayscale
img = cv2.imread(photo,0)

cv2.imshow("Test",img)

