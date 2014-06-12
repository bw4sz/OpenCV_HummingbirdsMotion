#make copy of the original image
img=display_image.copy()

#find edges
edges=cv2.Canny(img,100,150)

#find contours
contours,hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

cv2.namedWindow('contour', cv2.WINDOW_NORMAL)
cv2.imshow('contour',img)
for cnt in contours:
	bx,by,bw,bh = cv2.boundingRect(cnt)
	cv2.drawContours(img,[cnt],0,(0,255,0),1)   # draw #contours in green color
cv2.waitKey(1000)
cv2.destroyWindow("contour")

#get center_point
count=0
for x in range(1,len(contours)):
	dist = cv2.pointPolygonTest(contours[x],center_point,False)
	if dist == 1 :
		count=count+1
		cv2.drawContours(img,contours[x],0,(0,255,0),1)

cv2.imshow('contour',edges)
cv2.waitKey(100000)
cv2.destroyWindow("contour")	