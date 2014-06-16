import glob
images=glob.glob("C:/Users/Ben/Dropbox/Thesis/Maquipucuna_SantaLucia/FlowerPhotos/*.jpg")

for imag in images:
	       img=cv2.imread(imag)
	       #find edges
	       edges=cv2.Canny(img,100,250)
	       kernel = np.ones((3,3),np.uint8)
	       closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
	       
	       cv2.imshow('contour',closing)
	       cv2.waitKey(1000)
	       cv2.destroyWindow("contour")
	       #find contours
	       contours,hierarchy = cv2.findContours(closing,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	       
	       #sort contours
	       cnts = sorted(contours, key = cv2.contourArea, reverse = True)
	       
	       for cnt in cnts[]:
			      bx,by,bw,bh = cv2.boundingRect(cnt)
			      cv2.drawContours(img,[cnt],0,(0,255,0),1)   # draw #contours in green color
	       cv2.namedWindow('contour', cv2.WINDOW_NORMAL)
	       cv2.imshow('contour',img)
	       cv2.waitKey(1000)
	       cv2.destroyWindow("contour")
	       
	       #get center_point
	       #img=camera_imageROI.copy()
	       index=0
	       found=[]
	       for cnt in cnts:
			      dist = cv2.pointPolygonTest(cnt,center_point,False)
			      if dist == 1 :
					     found.append(index)
					     cv2.drawContours(img,[cnt],-1,(0,255,0),1)   # draw #contours in green color
					     for entity in this_frame_entity_list:
						     center_point = entity[3]
						     c = entity[1]  # RGB color tuple
						     cv2.circle(img, center_point,  5, (c[0], c[1], c[2]), 3)
			      index=index+1	
				       
	       cv2.imshow('contour',img)
	       cv2.waitKey(3000)
	       cv2.destroyWindow("contour")	
	       
	       
	       #Available contours to choose from.
	       foundcnts = [cnts[i] for i in found]
	       
	       #sort for size one more time, get the smallest one
	       cntsF = sorted(foundcnts, key = cv2.contourArea)
	       
	       desired_cnt=cntsF[0]
	       
	       #draw that contour to be sure
	       #img=camera_imageROI.copy()
	       cv2.drawContours(img,[desired_cnt],0,(0,255,0),1)   # draw #contours in green color
	       cv2.namedWindow('contour', cv2.WINDOW_NORMAL)
	       cv2.imshow('contour',img)
	       cv2.waitKey(1000)
	       cv2.destroyWindow("contour")