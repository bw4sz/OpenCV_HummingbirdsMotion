#Testing script to run a bunch of different command line cases to ensure motionmeerkat functionality.

import os

os.chdir('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/MotionMeerkat/')

#default
#os.system('main.py --i PlotwatcherTest.TLV')
#print('defaults: ok')

os.system('main.py --i PlotwatcherTest.TLV --thresh 0 --windy --windy_min 1')
print('min size: ok')
