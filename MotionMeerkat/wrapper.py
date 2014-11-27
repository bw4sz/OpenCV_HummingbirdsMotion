import report
import os
import traceback

########################################
###Run Analysis on a Pool of videos
########################################
def wrap(ob) :
        #quick error check.
        if ob.runtype=="file":
                if os.path.isfile(ob.inDEST): pass
                else:
                        print("File path does not exist!")
        else:
                if os.path.isdir(ob.batchpool): pass
                else:
                        print("Directory does not exist!")

        ###Run Batch Mode                
        if (ob.runtype == "batch"):
                ##Overall destination
                
                videoPool= []
                #Create Pool of Videos
                for (root, dirs, files) in os.walk(ob.batchpool):
                        for files in files:
                                if files.endswith((".TLV",".AVI",".avi",".MPG",".mp4",".MOD",".MTS",".wmv",".WMV",".mpg",".tlv")):
                                        videoPool.append(os.path.join(root, files))
                
                for vid in videoPool:      
                     
                        #Place run inside try catch loop; in case of error, step to next video
                        ##Run Motion Function
                        #override to set the inDEST file to loop from batch videos
                        ob.inDEST=vid
                        #try:
                        ob.prep()
                        ob.run()
                        ob.videoM()
                        report.report(ob)
                        #except Exception, e:
                                #print( "Error %s " % e + "\n" )
                                #print 'Error in Video:',vid

        ###If runtype is a single file - run file destination        
        if (ob.runtype == "file"):
                try:
                        ob.prep()
                        ob.run()
                        ob.videoM()
                        report.report(ob)                                
                except:
                        traceback.print_exc()
                        print 'Error in input file:',ob.inDEST