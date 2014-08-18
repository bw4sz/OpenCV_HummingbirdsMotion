from shapely.geometry import *
import cv2
import numpy
import random
import cProfile
import pstats


#current function
#Combine objects of motion bounding boxes
#Combine objects of motion bounding boxes
def merge_collided_bboxes(bbox_list ):
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
            
#we know the box list looks like

sam=[]
ft=[]
for x in range(1,100):
        xy=(random.randint(1,100),random.randint(1,100)),(random.randint(1,100),random.randint(1,100))
        sam.append((xy))
        ft.append(xy)
        
print len(sam)

top = 0
bottom = 1
left = 0
right = 1

##Profile code

cProfile.run("merge_collided_bboxes(sam)","merge.txt")

p = pstats.Stats('merge.txt')
p.sort_stats('cumulative').print_stats(20)

#To call total time, in case you want to compare
p.total_tt

#object reclass


##print "run"
##news=[]
##for rect1 in sp:
##    for rect2 in sp:
##        print rect1.intersection(rect2).area

##print news
from shapely.ops import cascaded_union
from shapely.prepared import prep

shape_list=[]

for out in ft:
    sh_out=box(out[0][0],out[0][1],out[1][0],out[1][1])
    shape_list.append(sh_out)

shape_pol=MultiPolygon(shape_list)
casc=cascaded_union(shape_pol)    

casc=cascaded_union(shape_list)    

print casc.type
shape_list=[]




def shape_try():
    for out in ft:
        sh_out=box(out[0][0],out[0][1],out[1][0],out[1][1])
        shape_list.append(sh_out)
        shape_pol=MultiPolygon(shape_list)
        casc=cascaded_union(shape_pol)
    return(casc)

cProfile.run("cas=shape_try","merge2.txt")

p = pstats.Stats('merge2.txt')
p.sort_stats('cumulative').print_stats(20)

#To call total time, in case you want to compare
p.total_tt

    
##if((rect1 & rect2) == rect1):
##    print "same"
##    # rect1 is completely inside rect2; do nothing.
##else:
##    if((rect1 & rect2).area() > 0):
##    #they intersect; merge the
##    newrect = rect1 | rect2
##    final_box.append(newrect)
##    

##
### Example grid cell
##gridcell_shape = box(129.5, -27.0, 129.75, 27.25)
### The intersection
##polygon_shape.intersection(gridcell_shape).area
##
##
##from shapely.ops import cascaded_union
##from rtree import index
##idx = index.Index()
##
### Populate R-tree index with bounds of grid cells
##for pos, cell in enumerate(grid_cells):
### assuming cell is a shapely object
##    idx.insert(pos, cell.bounds)
##
### Loop through each Shapely polygon
##for poly in polygons:
### Merge cells that have overlapping bounding boxes
##    merged_cells = cascaded_union([grid_cells[pos] for pos in idx.intersection(poly.bounds)])
##
### Now do actual intersection
##print poly.intersection(merged_cells).area
