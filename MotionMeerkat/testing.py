#Testing script to run a bunch of different command line cases to ensure motionmeerkat functionality.

import os

os.chdir('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/MotionMeerkat/')

#default
os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --subMethod MOG --moglearning 0.5 --makeVID frames --runtype batch')
#os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --subMethod MOG --moglearning 0.1 --makeVID none --runtype batch')
#os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --subMethod MOG --moglearning 0.01 --makeVID none --runtype batch')
#os.system('main.py --batchpool C:/Users/Ben/Desktop/MeerkatTest --subMethod MOG --moglearning 0.5 --makeVID none --runtype batch')

#print('defaults: ok')

#os.system('main.py --i C:/Users/Ben/Downloads/Betts.tlv --thresh 30 --minSIZE 0.3 --subMethod MOG --moglearning 0.1')
