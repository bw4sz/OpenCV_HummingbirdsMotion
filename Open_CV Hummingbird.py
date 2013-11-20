import cv2
import cv2.cv as cv
import numpy as np
import time
from scipy import *
from scipy.cluster import vq
import numpy
import sys, os, random, hashlib
import re
from math import *

"""
Python Motion Tracker

Reads an incoming video stream and tracks motion in real time.
Detected motion events are logged to a text file.  Also has face detection.
"""

#
# BBoxes must be in the format:
# ( (topleft_x), (topleft_y) ), ( (bottomright_x), (bottomright_y) ) )
top = 0
bottom = 1
left = 0
right = 1

def merge_collided_bboxes( bbox_list ):
        # For every bbox...
        for this_bbox in bbox_list:
                
                # Collision detect every other bbox:
                for other_bbox in bbox_list:
                        if this_bbox is other_bbox: continue  # Skip self
                        
                        # Assume a collision to start out with:
                        has_collision = True
                        
                        # These coords are in screen coords, so > means 
                        # "lower than" and "further right than".  And < 
                        # means "higher than" and "further left than".
                        
                        # We also inflate the box size by 10% to deal with
                        # fuzziness in the data.  (Without this, there are many times a bbox
                        # is short of overlap by just one or two pixels.)
                        if (this_bbox[bottom][0]*1.1 < other_bbox[top][0]*0.9): has_collision = False
                        if (this_bbox[top][0]*.9 > other_bbox[bottom][0]*1.1): has_collision = False
                        
                        if (this_bbox[right][1]*1.1 < other_bbox[left][1]*0.9): has_collision = False
                        if (this_bbox[left][1]*0.9 > other_bbox[right][1]*1.1): has_collision = False
                        
                        if has_collision:
                                # merge these two bboxes into one, then start over:
                                top_left_x = min( this_bbox[left][0], other_bbox[left][0] )
                                top_left_y = min( this_bbox[left][1], other_bbox[left][1] )
                                bottom_right_x = max( this_bbox[right][0], other_bbox[right][0] )
                                bottom_right_y = max( this_bbox[right][1], other_bbox[right][1] )
                                
                                new_bbox = ( (top_left_x, top_left_y), (bottom_right_x, bottom_right_y) )
                                
                                bbox_list.remove( this_bbox )
                                bbox_list.remove( other_bbox )
                                bbox_list.append( new_bbox )
                                
                                # Start over with the new list:
                                return merge_collided_bboxes( bbox_list )
        
        # When there are no collions between boxes, return that list:
        return bbox_list


def Target(fP):
        cap = cv2.VideoCapture(fP)
        frame = cap.read()[1]
        width = np.size(frame, 1)
        height = np.size(frame, 0)
        frame_size=(width, height)
        
        
        #Optionally show
        #cv2.imshow("frame",frame)
        #cv2.waitKey(100)
        #cv2.destroyWindow("frame")
        #Create directory and subdirectory
        ID = str.split(fP,"\\")[3]
        subD = str.split(str.split(fP,"\\")[4],".")[0]
    #Create a directory for output files
        if not os.path.exists(fileD+ID+"/"+subD):
                os.makedirs(fileD+ID+"/"+subD)
                
            
def run(fP,accAvg,threshL):
        ID = str.split(fP,"\\")[3]
        # Initialize
        #log_file_name = "tracker_output.log"
        #log_file = file( log_file_name, 'a' )
        
        cap = cv2.VideoCapture(fP)
            
        # Capture the first frame from file for image properties
        orig_image = cap.read()[1]  
        
        #For now, just cut off the bottom 5% ####NEEDS TO BE CHANGED
        display_image = orig_image[1:700,1:1280]
        #cv2.imshow("frame",display_image)
        #cv2.waitKey(1000)
        #cv2.destroyWindow("frame")        

        #Define SubArea Based on Mouse Event   
        box=[0,0,0,0]
        
        ##        creating mouse callback function
        #def my_mouse_callback(event,x,y,flags,param):
                #global drawing_box
                #if event==cv2.EVENT_LBUTTONDOWN:
                        #drawing_box=True
                        #[box[0],box[1],box[2],box[3]]=[x,y,0,0]
                        #print box[0]
        
                #if event==cv2.EVENT_LBUTTONUP:
                        #drawing_box=False
                        #if box[2]<0:
                                #box[0]+=box[2]
                                #box[2]*=-1
                        #if box[3]<0:
                                #box[1]+=box[3]
                                #box[3]*=-1
                                
                #if event==cv2.EVENT_MOUSEMOVE:
                        #if (drawing_box==True):
                                #box[2]=x-box[0]
                                #box[3]=y-box[1]        
                        
        ## Function to draw the rectangle                
        #def draw_box(img,box):
                #cv2.rectangle(img,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(255,0,0))
        
        ##        main program        
        #drawing_box=False              
        #cv2.namedWindow("Box Example")
        #cv2.setMouseCallback("Box Example",my_mouse_callback,display_image)
        
        #while(1):
                #temp=display_image.copy()
                #if drawing_box==True:
                        #draw_box(temp,box)
                #cv2.imshow("Box Example",temp)
                #if cv.WaitKey(20)%0x100==27:break

        #cv2.destroyWindow("Box Example")                

##################################################################################################
#For now, just have it ignore the bottom few rows, since that is where the time diff is being sent.
##################################################################################################

        width = np.size(display_image, 1)
        height = np.size(display_image, 0)
        frame_size=(width, height)
        
        # Greyscale image, thresholded to create the motion mask:
        grey_image = np.uint8(display_image)
        
        # The RunningAvg() function requires a 32-bit or 64-bit image...
        running_average_image = np.float32(display_image)
        
        # ...but the AbsDiff() function requires matching image depths:
        running_average_in_display_color_depth = display_image.copy()
        
        # RAM used by FindContours():
        mem_storage = cv.CreateMemStorage(0)
        
        # The difference between the running average and the current frame:
        difference =  display_image.copy()
        
        target_count = 1
        last_target_count = 1
        last_target_change_t = 0.0
        k_or_guess = 1
        codebook=[]
        frame_count=0
        last_frame_entity_list = []
        
        t0 = time.time()
        
        # For toggling display:
        image_list = [ "camera", "difference", "threshold", "display", "faces" ]
        image_index = 0   # Index into image_list
        
        # Prep for text drawing:
        text_font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX, .5, .5, 0.0, 1, cv.CV_AA )
        text_coord = ( 5, 15 )
        text_color = (255,255,255)

        # Set this to the max number of targets to look for (passed to k-means):
        max_targets = 1
                
        while True:
                
                # Capture frame from file
                ret,camera_imageO = cap.read()
                if not ret:
                        break    
                
                #For now, just cut off the bottom 5% ####NEEDS TO BE CHANGED
                camera_image = camera_imageO[1:700,1:1280]                
                frame_count += 1
                frame_t0 = time.time()
                              
                # Create an image with interactive feedback:
                display_image = camera_image.copy()
                
                # Create a working "color image" to modify / blur
                color_image =  display_image.copy()
                #cv2.imshow("Initial",color_image)
                #cv2.waitKey(1000)
                #cv2.destroyWindow("Initial")                        

                # Smooth to get rid of false positives
                color_image = cv2.GaussianBlur(color_image,(9,9),0)
                #cv2.imshow("Blur",color_image)
                #cv2.waitKey(1000)
                #cv2.destroyWindow("Blur")  
                
                # Use the Running Average as the static background                        
                # a = 0.020 leaves artifacts lingering way too long.
                # a = 0.320 works well at 320x240, 15fps.  (1/a is roughly num frames.)
                #This value is very critical.
                                       
                cv2.accumulateWeighted(color_image,running_average_image,accAvg)
                #cv2.imshow("frame",running_average_image)
                ##cv2.waitKey(100)
                #cv2.destroyWindow("frame")                                       
                                       
                running_average_in_display_color_depth = cv2.convertScaleAbs( running_average_image)
                #cv2.imshow("runnAVG",running_average_in_display_color_depth)
                #cv2.waitKey(1000)
                #cv2.destroyWindow("runnAVG")                        
                
                # Subtract the current frame from the moving average.
                difference=cv2.absdiff( color_image, running_average_in_display_color_depth)
                #cv2.imshow("diff",difference)
                #cv2.waitKey(1000)
                #cv2.destroyWindow("diff")
                
                # Convert the image to greyscale.
                grey_image=cv2.cvtColor( difference,cv2.COLOR_BGR2GRAY)
                #cv2.imshow("Convertgray",grey_image)
                #cv2.waitKey(100)
                #cv2.destroyWindow("Convertgray")
                
                # Threshold the image to a black and white motion mask:
                ret,grey_image = cv2.threshold(grey_image, threshL, 255, cv2.THRESH_BINARY )
                #cv2.imshow("Threshold",grey_image)
                #cv2.waitKey(1000)
                #cv2.destroyWindow("Threshold")
                
                # Smooth and threshold again to eliminate "sparkles"
                #grey_image = cv2.GaussianBlur(grey_image,(9,9),0)    
                #ret,grey_image = cv2.threshold(grey_image, 240, 255, cv2.THRESH_BINARY )
                #cv2.imshow("frame",grey_image)
                #cv2.waitKey(1000)
                #cv2.destroyWindow("frame") 
                
                non_black_coords_array = numpy.where( grey_image > 3 )
                # Convert from numpy.where()'s two separate lists to one list of (x, y) tuples:
                non_black_coords_array = zip( non_black_coords_array[1], non_black_coords_array[0] )
                
                points = []   # Was using this to hold either pixel coords or polygon coords.
                bounding_box_list = []

                # Now calculate movements using the white pixels as "motion" data
                contours,hierarchy = cv2.findContours(grey_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE )
                
                if len(contours) == 0 :
                        continue                        
                print(len(contours))
                cnt=contours[0]
                len(cnt)
                        
                       
                        
                drawing = np.uint8(display_image)
                
                ##Draw the initial contours?
                #for cnt in contours:
                        #bx,by,bw,bh = cv2.boundingRect(cnt)
                        #cv2.drawContours(drawing,[cnt],0,(0,255,0),1)   # draw contours in green color
                        #cv2.imshow('output',drawing)
                        ##cv2.waitKey(100)
                        
    
                cv2.destroyWindow("output")
                
                for cnt in contours:
                        
                        bounding_rect = cv2.boundingRect( cnt )
                        point1 = ( bounding_rect[0], bounding_rect[1] )
                        point2 = ( bounding_rect[0] + bounding_rect[2], bounding_rect[1] + bounding_rect[3] )
                        
                        bounding_box_list.append( ( point1, point2 ) )
                        polygon_points = cv2.approxPolyDP( cnt,0.1*cv2.arcLength(cnt,True),True)
                        approx = cv2.approxPolyDP(cnt,0.1*cv2.arcLength(cnt,True),True)
                        
                        ## To track polygon points only (instead of every pixel):
                        ##points += list(polygon_points)
                        
                        ## Draw the contours:
                        ##cv.DrawContours(color_image, contour, cv.CV_RGB(255,0,0), cv.CV_RGB(0,255,0), levels, 3, 0, (0,0) )
                        
                        ##cv.FillPoly( grey_image, [ list(polygon_points), ], cv.CV_RGB(255,255,255), 0, 0 )
                        ##cv.PolyLine( display_image, [ polygon_points, ], 0, cv.CV_RGB(255,255,255), 1, 0, 0 )
                        
                        ##cv.Rectangle( display_image, point1, point2, cv.CV_RGB(120,120,120), 1)

                        ##contour = contour.h_next()
                
                
                # Find the average size of the bbox (targets), then
                # remove any tiny bboxes (which are prolly just noise).
                # "Tiny" is defined as any box with 1/10th the area of the average box.
                # This reduces false positives on tiny "sparkles" noise.
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
                        
                        # Only keep the box if it's not a tiny noise box:
                        if (box_width * box_height) > average_box_area*0.1: trimmed_box_list.append( box )
                
                ## Draw the trimmed box list:
                #print(len(trimmed_box_list))
                #for box in trimmed_box_list:
                        #cv2.rectangle( display_image, box[0], box[1], (0,255,0), 3 )
                        #cv2.imshow('output',display_image)
                        ##cv2.waitKey(100)    
                #cv2.destroyWindow("output")
                        
                bounding_box_list = merge_collided_bboxes( trimmed_box_list )

                # Draw the merged box list:
                
                for box in bounding_box_list:
                        cv2.rectangle( display_image, box[0], box[1], (0,255,0), 1 )
                        #cv2.imshow('output',orig_image)
                #cv2.waitKey(1000)  
                #cv2.destroyWindow("output")
                        
                # Here are our estimate points to track, based on merged & trimmed boxes:
                estimated_target_count = len( bounding_box_list )
                
                # Don't allow target "jumps" from few to many or many to few.
                # Only change the number of targets up to one target per n seconds.
                # This fixes the "exploding number of targets" when something stops moving
                # and the motion erodes to disparate little puddles all over the place.
                
                if frame_t0 - last_target_change_t < .350:  # 1 change per 0.35 secs
                        estimated_target_count = last_target_count
                else:
                        if last_target_count - estimated_target_count > 1: estimated_target_count = last_target_count - 1
                        if estimated_target_count - last_target_count > 1: estimated_target_count = last_target_count + 1
                        last_target_change_t = frame_t0
                
                # Clip to the user-supplied maximum:
                estimated_target_count = min( estimated_target_count, max_targets )
                
                # The estimated_target_count at this point is the maximum number of targets
                # we want to look for.  If kmeans decides that one of our candidate
                # bboxes is not actually a target, we remove it from the target list below.
                
                # Using the numpy values directly (treating all pixels as points):        
                points = non_black_coords_array
                center_points = []
                        
                if len(points):
                        
                        # If we have all the "target_count" targets from last frame,
                        # use the previously known targets (for greater accuracy).
                        k_or_guess = max( estimated_target_count, 1 )  # Need at least one target to look for.
                        if len(codebook) == estimated_target_count: 
                                k_or_guess = codebook
                        
                        #points = vq.whiten(array( points ))  # Don't do this!  Ruins everything.
                        codebook, distortion = vq.kmeans( array( points ), k_or_guess )
                        
                        # Convert to tuples (and draw it to screen)
                        for center_point in codebook:
                                center_point = ( int(center_point[0]), int(center_point[1]) )
                                center_points.append( center_point )
                                cv2.circle(display_image, center_point, 10, (255, 0, 0), 2)
                                cv2.circle(display_image, center_point, 5, (255, 0, 0), 3)
                                #cv2.imshow('output',orig_image)
                                #cv2.waitKey(500)  
                        #cv2.destroyWindow("output")                        
                # Now we have targets that are NOT computed from bboxes -- just
                # movement weights (according to kmeans).  If any two targets are
                # within the same "bbox count", average them into a single target.  
                #
                # (Any kmeans targets not within a bbox are also kept.)
                trimmed_center_points = []
                removed_center_points = []
                                        
                for box in bounding_box_list:
                        # Find the centers within this box:
                        center_points_in_box = []
                        
                        for center_point in center_points:
                                if        center_point[0] < box[right][0] and center_point[0] > box[left][0] and \
                                        center_point[1] < box[bottom][1] and center_point[1] > box[top][1] :
                                        
                                        # This point is within the box.
                                        center_points_in_box.append( center_point )
                        
                        # Now see if there are more than one.  If so, merge them.
                        if len( center_points_in_box ) > 1:
                                # Merge them:
                                x_list = y_list = []
                                for point in center_points_in_box:
                                        x_list.append(point[0])
                                        y_list.append(point[1])
                                
                                average_x = int( float(sum( x_list )) / len( x_list ) )
                                average_y = int( float(sum( y_list )) / len( y_list ) )
                                
                                trimmed_center_points.append( (average_x, average_y) )
                                
                                # Record that they were removed:
                                removed_center_points += center_points_in_box
                                
                        if len( center_points_in_box ) == 1:
                                trimmed_center_points.append( center_points_in_box[0] ) # Just use it.
                
                # If there are any center_points not within a bbox, just use them.
                # (It's probably a cluster comprised of a bunch of small bboxes.)
                for center_point in center_points:
                        if (not center_point in trimmed_center_points) and (not center_point in removed_center_points):
                                trimmed_center_points.append( center_point )
                
                # Draw what we found:
                #for center_point in trimmed_center_points:
                #        center_point = ( int(center_point[0]), int(center_point[1]) )
                #        cv2.circle(display_image, center_point, 20, (255, 255,255), 1)
                #        cv2.circle(display_image, center_point, 15, (100, 255, 255), 1)
                #        cv2.circle(display_image, center_point, 10, (255, 255, 255), 2)
                #        cv2.circle(display_image, center_point, 5,(100, 255, 255), 3)
                
                # Determine if there are any new (or lost) targets:
                actual_target_count = len( trimmed_center_points )
                last_target_count = actual_target_count
                
                # Now build the list of physical entities (objects)
                this_frame_entity_list = []
                
                # An entity is list: [ name, color, last_time_seen, last_known_coords ]
                
                for target in trimmed_center_points:
                        
                        # Is this a target near a prior entity (same physical entity)?
                        entity_found = False
                        entity_distance_dict = {}
                        
                        for entity in last_frame_entity_list:
                                
                                entity_coords= entity[3]
                                delta_x = entity_coords[0] - target[0]
                                delta_y = entity_coords[1] - target[1]
                
                                distance = sqrt( pow(delta_x,2) + pow( delta_y,2) )
                                entity_distance_dict[ distance ] = entity
                        
                        # Did we find any non-claimed entities (nearest to furthest):
                        distance_list = entity_distance_dict.keys()
                        distance_list.sort()
                        
                        for distance in distance_list:
                                
                                # Yes; see if we can claim the nearest one:
                                nearest_possible_entity = entity_distance_dict[ distance ]
                                
                                # Don't consider entities that are already claimed:
                                if nearest_possible_entity in this_frame_entity_list:
                                        #print "Target %s: Skipping the one iwth distance: %d at %s, C:%s" % (target, distance, nearest_possible_entity[3], nearest_possible_entity[1] )
                                        continue
                                
                                #print "Target %s: USING the one iwth distance: %d at %s, C:%s" % (target, distance, nearest_possible_entity[3] , nearest_possible_entity[1])
                                # Found the nearest entity to claim:
                                entity_found = True
                                nearest_possible_entity[2] = frame_t0  # Update last_time_seen
                                nearest_possible_entity[3] = target  # Update the new location
                                this_frame_entity_list.append( nearest_possible_entity )
                                #log_file.write( "%.3f MOVED %s %d %d\n" % ( frame_t0, nearest_possible_entity[0], nearest_possible_entity[3][0], nearest_possible_entity[3][1]  ) )
                                break
                        
                        if entity_found == False:
                                # It's a new entity.
                                color = ( random.randint(0,255), random.randint(0,255), random.randint(0,255) )
                                name = hashlib.md5( str(frame_t0) + str(color) ).hexdigest()[:6]
                                last_time_seen = frame_t0
                                
                                new_entity = [ name, color, last_time_seen, target ]
                                this_frame_entity_list.append( new_entity )
                                #log_file.write( "%.3f FOUND %s %d %d\n" % ( frame_t0, new_entity[0], new_entity[3][0], new_entity[3][1]  ) )
                
                # Now "delete" any not-found entities which have expired:
                entity_ttl = 1.0  # 1 sec.
                
                for entity in last_frame_entity_list:
                        last_time_seen = entity[2]
                        if frame_t0 - last_time_seen > entity_ttl:
                                # It's gone.
                                #log_file.write( "%.3f STOPD %s %d %d\n" % ( frame_t0, entity[0], entity[3][0], entity[3][1]  ) )
                                pass
                        else:
                                # Save it for next time... not expired yet:
                                this_frame_entity_list.append( entity )
                
                # For next frame:
                last_frame_entity_list = this_frame_entity_list
                
                # Draw the found entities to screen:
                for entity in this_frame_entity_list:
                        center_point = entity[3]
                        c = entity[1]  # RGB color tuple
                        cv2.circle(camera_imageO, center_point, 20, (c[0], c[1], c[2]), 1)
                        cv2.circle(camera_imageO, center_point, 15, (c[0], c[1], c[2]), 1)
                        cv2.circle(camera_imageO, center_point, 10, (c[0], c[1], c[2]), 2)
                        cv2.circle(camera_imageO, center_point,  5, (c[0], c[1], c[2]), 3)
                #cv2.imshow('output',camera_imageO)
                #cv2.waitKey(1000)  
                #cv2.destroyWindow("output")                                     

                ###print ("min_size is: " + str(min_size))
                ### Listen for ESC or ENTER key
                #c = cv.WaitKey(7) % 0x100
                #if c == 27 or c == 10:
                        #break
                
                ## Toggle which image to show
                #if chr(c) == 'd':
                        #image_index = ( image_index + 1 ) % len( image_list )
                
                #image_name = image_list[ image_index ]
                
                ## Display frame to user
                #if image_name == "camera":
                        #image = camera_image
                        #cv2.putText( image, "Camera (Normal)", text_coord, text_font, text_color )
                #elif image_name == "difference":
                        #image = difference
                        #cv2.putText( image, "Difference Image", text_coord, text_font, text_color )
                #elif image_name == "display":
                        #image = display_image
                        #cv2.putText( image, "Targets (w/AABBs and contours)", text_coord, text_font, text_color )
                #elif image_name == "threshold":
                        ## Convert the image to color.
                        #cv.CvtColor( grey_image, display_image, cv.CV_GRAY2RGB )
                        #image = display_image  # Re-use display image here
                        #cv2.putText( image, "Motion Mask", text_coord, text_font, text_color )
            
                
                ##cv2.ShowImage( "Target", image )
                #cv2.imshow("Target",image)
                #cv2.waitKey(1000)
                #cv2.destroyWindow("frame")                        
                
                ##################################################
                #To Do, write to file if the center is in the box?
                #If it makes it to here, write an image
                cv2.imwrite(fileD+ID+"/"+str(frame_count)+".jpg",camera_imageO)
                
                ##################################################
                
                
                ##log_file.flush()
                
                ## If only using a camera, then there is no time.sleep() needed, 
                ## because the camera clips us to 15 fps.  But if reading from a file,
                ## we need this to keep the time-based target clipping correct:
                #frame_t1 = time.time()
                
                ### If reading from a file, put in a forced delay:
                ##if not self.writer:
                        ##delta_t = frame_t1 - frame_t0
                        ##if delta_t < ( 1.0 / 15.0 ): time.sleep( ( 1.0 / 15.0 ) - delta_t )
                        
        #t1 = time.time()
        #time_delta = t1 - t0
        #processed_fps = float( frame_count ) / time_delta
        #print "Got %d frames. %.1f s. %f fps." % ( frame_count, time_delta, processed_fps )


####################################################################################################
#Run Analysis
####################################################################################################

videoPool= []
#Create Pool of Videos
for root, dirs, files in os.walk("F:\\SantaLucia2\\Flowers\\"):
        for file in files:
                if file.endswith(".TLV"):
                        videoPool.append( os.path.join(root, file))


#Set location of the file directory for output. 
fileD="C:/Users/Jorge/Dropbox/Thesis/Maquipucuna_SantaLucia/MotionTest/"


string1= "F:/SantaLucia2/Flowers/FL072/130726AA.tlv"
obj1 = re.search('',string1)
print(obj1.group(1))

#fullPath="F:/SantaLucia2/Flowers/FL072/130726AA.tlv"
##Set the file path to video
##The first arguement is the filepath of the video
##The second argument is the name of the output folder.

##Set output directory name
ID="Test1"

Target(fullPath)

##Run Motion Function
##The first arguement is the filepath of the video
##The second argument is the accumlated averaging, higher values are more sensitive to sudden movements
##The third value is the thresholding, a way of differentiating the background from movement, higher values (0-255) disregard more motion, lower values make the model more sensitive to motion

run(fullPath,.4,40)


#############Run a few for the weekend

#fullPath=
#ID="FL078"
#Target(fullPath,ID)
#run(fullPath,.4,40,ID)

###################Try a new flower
#fullPath=
#ID="FL078_T40"
#Target(fullPath,ID)
#run(fullPath,.4,40,ID)

####Same flower, twice the threshold.
#fullPath="F:/SantaLucia2/Flowers/FL090/130801AA.TLV"
#ID="FL090_T80"
#Target(fullPath,ID)
#run(fullPath,.4,80,ID)


###Same flower, twice the threshold.
fullPath="F:/SantaLucia2/Flowers/FL090/130801AA.TLV"
ID="FL090_T40"
Target(fullPath,ID)
run(fullPath,.4,40,ID)


###Same flower, twice the threshold.
fullPath="F:/SantaLucia2/Flowers/FL090/130801AA.TLV"
ID="FL090_AGG2"
Target(fullPath,ID)
run(fullPath,.2,40,ID)


###Same flower, twice the threshold.
fullPath="F:/SantaLucia2/Flowers/FL090/130801AA.TLV"
ID="FL090_AGG9"
Target(fullPath,ID)
run(fullPath,.9,40,ID)


########################Try a new flower, really awful flower

#fullPath="F:/SantaLucia2/Flowers/FL081/130727AB.TLV"
#ID="FL081"
#Target(fullPath,ID)
#run(fullPath,.4,40,ID)

########################## One more flower
#fullPath="F:/SantaLucia2/Flowers/FL083/130730AA.TLV"
#ID="FL083_AGG4"
#Target(fullPath,ID)
#run(fullPath,.4,40,ID)

########################## Same flower, double the background averaging
#fullPath="F:/SantaLucia2/Flowers/FL083/130730AA.TLV"
#ID="FL083_AGG8"
#Target(fullPath,ID)
#run(fullPath,.8,40,ID)



#Destroy Windows
cv2.destroyAllWindows()