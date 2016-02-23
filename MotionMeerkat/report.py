import time
import csv
import cv2
import Plotting

def report(ob):
        
        #Run is over, destroy display windows
        cv2.destroyAllWindows()
        
        #Create log file
        log_file_report = ob.file_destination + "/" + "Parameters_Results.log"
        log_report = file(log_file_report, 'a' )

        #Print parameters
        #Batch or single file
        log_report.write("Input Parameters")        
        log_report.write("\nRun type: %s" % ob.runtype)
        if ob.runtype in ["file","pictures"]:
                log_report.write("\nInput file path: %s" % ob.inDEST)
                
        else:
                log_report.write("\nInput file path: %s" % ob.batchpool)
        log_report.write("\nOutput dir: %s" % ob.fileD)
        log_report.write("\nBackground Subtraction Method?: %s" % ob.subMethod)
        
        if ob.subMethod == "MOG":
                log_report.write("\nLearning Rate: %s" % ob.moglearning)
                log_report.write("\nVariance Rate: %s" % ob.mogvariance)
        
        if ob.subMethod == "Acc":
                log_report.write("\nAccumulated Averaging: %s" % ob.accAvg)  
                log_report.write("\nAdapt Parameters: %s" % ob.adapt)                

        if ob.adapt:
                log_report.write("\nExpected hitrate: %s" % ob.frameHIT)
                log_report.write("\nMinimum accAvg: %s" % ob.floorvalue)
        
        log_report.write("\nThreshold: %s" % ob.threshT)
        log_report.write("\nMinimum contour area: %s" % ob.minSIZE)
        if ob.burnin > 0:
                log_report.write("\nBurnin: %s" % ob.burnin)
        if ob.scan > 0:
                log_report.write("\nScan frames: %s" % ob.scan)
        if ob.frameSET:
                log_report.write("\nManual framerate: %s" % ob.frame_rate)
        if ob.set_ROI:        
                log_report.write("\nSet ROI: %s" % ob.ROI_include)
        if ob.set_areacounter:
                log_report.write("\nArea counter: %s" % ob.set_areacounter)
        log_report.write("\nOutput type: %s\n\n" % ob.makeVID)

        #Ending time
        end=time.time()

        #total_time()
        total_min=(end-ob.start)/60

        #processed frames per second
        pfps=float(ob.frame_count)/(total_min*60)

        ##Write to log file
        log_report.write("Processing\n")        
        log_report.write("Total run time (min): %.2f \n" % total_min)
        log_report.write("Average frames per second: %.2f \n " % pfps)

        #End of program, report some statistic to screen and log
        #log
        log_report.write("\nResults\n")
        log_report.write("Candidate motion events: %.0f \n" % ob.total_count )
        log_report.write("Frames skipped due to insufficient movement based on the threshold parameter: %.0f \n" % ob.nocountr)
        log_report.write("Frames skipped due to minimum size of the contours: %.0f \n" % ob.toosmall)
        if ob.windy:
                log_report.write("Frames skipped due to windy conditions: %.0f \n" % ob.windy_count)                
        log_report.write("Total frames in files: %.0f \n" % ob.frame_count)
        
        rate=float(ob.total_count)/ob.frame_count*100
        log_report.write("Hitrate: %.2f %% \n" % rate)

        #print to screen
        print("\n\nThank you for using MotionMeerkat! \n")
        print("Total run time (min): %.2f \n " % total_min)
        print("Average frames processed per second: %.2f \n " % pfps)   
        print("Candidate motion events: %.0f \n " % ob.total_count )
        print("Frames skipped due to insufficient movement based on the threshold parameter: %.0f \n " % ob.nocountr)
        print("Frames skipped due to minimum size of the contours: %.0f \n " % ob.toosmall)
        
        #if windy
        if ob.windy:
                print("Frames skipped due to windy conditions: %.0f \n " % ob.windy_count)
                
        print("Total frames in files: %.0f \n " % ob.frame_count)

        rate=float(ob.total_count)/ob.frame_count*100
        print("Hitrate: %.2f %% \n" % rate)
        
        
        ####Generate plots
        #Show box size by area
        if ob.runtype == 'file':
                tarea=(ob.width * ob.height)
                scale_size=[x/tarea for x in ob.avg_area]
                #First frame is artifact of intilization
                scale_size[0]=None
                Plotting.combineplots(scale_size,ob.frame_results,ob.minSIZE,ob.file_destination + "/" + "Diagnostics.png")
        
        #reset frame count if in batch loop
        ob.frame_count=0
        ob.total_count=0
        ob.toosmall=0
        ob.nocountr=0
        
        #Write csv of time stamps and frame counts
        #file name
        time_stamp_report = ob.file_destination + "/" + "Frames.csv"

        with open(time_stamp_report, 'wb') as f:
                writer = csv.writer(f)
                writer.writerows(ob.stamp)
        if ob.set_areacounter:
                area_report = ob.file_destination + "/" + "AreaCounter.csv"
                with open(area_report, 'wb') as f:
                        writer = csv.writer(f)
                        writer.writerows(ob.areaC)