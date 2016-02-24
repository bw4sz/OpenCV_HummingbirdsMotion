import numpy as np
import glob
import os

def remove_singletons(frame_results,distance,destination):
    
    #index list
    index_frame=range(0,len(frame_results))
    only_true_frames=np.array(index_frame)[np.array(frame_results)]
    
    print(frame_results)
    
    sf=np.sort(only_true_frames)
    
    #Forwards
    forwards=abs(np.diff(sf))
    #add back in the first number     
    full_forwards=np.hstack([abs(sf[0]-sf[1]),forwards])
    
    #Backwards
    backwards=abs(np.diff(sf[::-1]))
    full_backwards=np.hstack([abs(sf[::-1][0]-sf[::-1][1]),forwards])
    
    both = []
    for x in range(0,len(full_forwards)):
        both.append(min(full_forwards[x],full_backwards[x]))
    
    #which are outside the distances
    b=[x > distance for x in both]
    
    #What are the indices that need to be removed.
    todel=np.array(only_true_frames)[np.array(b)]

    #However, the array are 0 indexed. The frames are 1 indexed. The first frame is frame #1, "1.jpg"
    todelframes=[x+1 for x in todel]
    
    #Counter
    counter=0
    for x in todelframes: 
        f=destination + "/" + str(x) + ".jpg"        
        if os.path.exists(f): 
            os.remove(f)
            counter=counter + 1
    return(counter)

def remove_init(learning_wait,frame_rate,length_results):
#If time lapse delay the beginning of motion detection
    #If its time lapse, 
    if frame_rate ==1:
        #If the video is twice as long as the init period
        if length_results > frame_rate * learning_wait * 60 * 2: 
            print("Frame rate is 1 fps, MOG detector needs a couple moments to initialize.\n Removing frames outputting during initilization. This can be changed by setting the learning_wait parameter in advanced settings\n")
            todel = range(1,frame_rate * learning_wait * 60)
            counter=0
            for x in todel: 
                f=destination + "/" + str(x) + ".jpg"        
                if os.path.exists(f): 
                    os.remove(f)
                    counter=counter + 1
            print("%d motion frames removed due initilization period of %d minutes" % (counter, learning_wait))  
            return(counter)                
