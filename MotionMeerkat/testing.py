#Testing script to run a bunch of different command line cases to ensure motionmeerkat functionality.

import os

#cd into direction holding main.py - for users this would be the directory holding main.exe

# Run from command line, using default video to test state
testing_mainpy = False
if testing_mainpy:
    os.chdir('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/MotionMeerkat/')
    
    #Minsize
    os.system('main.py --minSIZE 0.3')
    
    #Threshold
    os.system('main.py --thresh 10')
    
    #Cropping
    os.system('main.py --set_ROI --ROI_include include')
    
    #Change frame rate
    os.system('main.py --frameSET --frame_rate 1')
    
    #Windy conditions
    os.system('main.py --windy --windy_min 1')
    
    #Burnin by 0.1 minute
    #os.system('main.py --burnin 1')
    
    #Skip every other frame
    os.system('main.py --scan 1')
    
    #Change background subtractor
    os.system('main.py --subMethod Acc --accAvg 0.4 --adapt')

testing_mainexe = True
if testing_mainexe:
    os.chdir('C:/Program Files (x86)/MotionMeerkat/')
    
    #Minsize
    os.system('main.exe --minSIZE 0.3')
    
    #Threshold
    os.system('main.exe --thresh 10')
    
    #Cropping
    os.system('main.exe --set_ROI --ROI_include include')
    
    #Change frame rate
    os.system('main.exe --frameSET --frame_rate 1')
    
    #Windy conditions
    os.system('main.exe --windy --windy_min 1')
    
    #Burnin by 0.1 minute
    os.system('main.exe --burnin 1')
    
    #Skip every other frame
    os.system('main.exe --scan 1')
    
    #Change background subtractor
    os.system('main.exe --subMethod Acc --accAvg 0.4 --adapt')
