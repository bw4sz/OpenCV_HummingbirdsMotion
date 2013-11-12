import cv2
import numpy as np


# Load an color image in grayscale
img = cv2.imread('C:/Users/Ben/Dropbox/Thesis/Maquipucuna_SantaLucia/FlowerPhotos/17.jpg',cv2.CV_LOAD_IMAGE_COLOR)

cv2.namedWindow("image", 1)
cv2.imshow('image',img)
cv2.waitKey(10)
