#Set location of the file directory
fileD="C:/Users/Jorge/Documents/OpenCV_HummingbirdsMotion/"

#Set the file path to video

fP=fileD+"PlotwatcherTest.tlv"

cap = cv2.VideoCapture(fP)
total_frames=cap.get(cv.CV_CAP_PROP_FOURCC)
cap.get(cv.CV_CAP_PROP_FPS)

frame = []

ret,camera_imageO = cap.read()

width = np.size(camera_imageO, 1)
height = np.size(camera_imageO, 0)
frame_size=(width, height)

for g in range(0,20):
    ret,camera_imageO = cap.read()
    frame.append(camera_imageO)

video = cv2.VideoWriter("C:/Users/Jorge/Documents/OpenCV_HummingbirdsMotion/test11.avi", cv2.cv.CV_FOURCC('F','M','P', '4'),10, frame_size, 1)

for f in frame:
    video.write(f)                                

