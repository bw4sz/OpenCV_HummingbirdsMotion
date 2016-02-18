#Testing script to run a bunch of different command line cases to ensure motionmeerkat functionality.

import os

os.chdir('C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/MotionMeerkat/dist/main')

#default
os.system('main.exe --i PlotwatcherTest.TLV')
print('defaults: ok')

#Changing each of the main settings
os.system('main.exe --i PlotwatcherTest.TLV --min 0.5')
print('min size: ok')
