#Testing script to run a bunch of different command line cases to ensure motionmeerkat functionality.

import os

#cd into direction holding main.py - for users this would be the directory holding main.exe
os.chdir('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/MotionMeerkat/')

# Run from command line
# Note: for users without source code, replace main.py with main.exe.
#os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --fileD C:/MotionMeerkat/MOG --subMethod MOG --moglearning 0.1 --makeVID frames --runtype batch --windy --windy_min 1')
#os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --fileD C:/MotionMeerkat/Acc --subMethod Acc --moglearning 0.1 --makeVID frames --runtype batch --windy --windy_min 1')

os.system('main.py --i C:/Users/Ben/Desktop/MeerkatTest/MoyTest.mpg --subMethod MOG --moglearning 0.1')

#print('defaults: ok')

#os.system('main.py --i C:/Users/Ben/Downloads/Betts.tlv --thresh 30 --minSIZE 0.3 --subMethod MOG --moglearning 0.1')
