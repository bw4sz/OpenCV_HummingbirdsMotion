#Testing script to run a bunch of different command line cases to ensure motionmeerkat functionality.

import os

#cd into direction holding main.py - for users this would be the directory holding main.exe
os.chdir('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/MotionMeerkat/')

# Run from command line, using default video to test state
testing = False
if testing:
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
    os.system('main.py --burnin 1')
    
    #Skip every other frame
    os.system('main.py --scan 1')
    
    #Change background subtractor
os.system('main.py --subMethod Acc --accAvg 0.4 --adapt')


# Note: for users without source code, replace main.py with main.exe.
#os.system('main.py --windy --i C:/Users/Ben/Desktop/MeerkatTest/MoyTest.mpg')
#os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --fileD C:/MotionMeerkat/MOG --runtype batch --makeVID none')
#os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --fileD C:/MotionMeerkat/Acc --subMethod Acc --moglearning 0.1 --makeVID frames --runtype batch --windy --windy_min 1')

#os.system('main.py --i C:/Users/Ben/Desktop/MeerkatTest/MoyTest.mpg --subMethod MOG --moglearning 0.1')

#print('defaults: ok')

#os.system('main.py --i C:/Users/Ben/Downloads/Betts.tlv --thresh 30 --minSIZE 0.3 --subMethod MOG --moglearning 0.1')
