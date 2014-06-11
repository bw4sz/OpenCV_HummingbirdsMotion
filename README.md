OpenCV_HummingbirdsMotion
-----------------------------

Technical Aim: Identify which frames in a video have motion and save them to file.
Use: We have been studying hummingbird plant pollination in North Ecuador. Using innovative camera traps that record images once per second, we have developed a databank of 3.5 tb of flower videos. On average, 3-5 birds visit the flowers every 6 hours. Instead of manually reviewing the videos, we are designing software using python and open_CV to analyse the videos

If you have ideas about how to do this, i'd love feedback! Please fork and try it yourself, test files are included in this repository, as well as still frame image ("17") about the desired output

Approach
-------------

Combining Python 2.7 and the OpenCv2 library, with videos read using ffmpeg. 

All testing has been done on Windows, but there is no reason to expect major difficulties on linux or mac.

Contents
-------------
/dist: folder containing the executable dist build
/build: data files for executable
/testing: A collection small files (video, images) and test scripts to open up and image, test the codec reading. Also contains a PlotwatcherTest.tlv which contains a known motion event (hummingbird visiting flower)
/Bisque_Dev: Module for Iplant's BISQUE Bio-image analysis center. This code cannot be run from source, and is only to connect to the BISQUE API
/Ranalysis: R scripts to process and make figures for publication
/Results: Folder to hold all the figures made in R
Motion.py: Core function. A Python script which takes in video file and parameters, and returns candidate motion frames.

Motion.py
-----------
Python executable - can be run from shell or IDLE, first time users should just open .py file up in IDLE (or any python interpreter)

When run inline, program will ask for the arguments:

Arguments:
File/batch mode,
file input, 
file destination, 
sensitivity parameter, 
True/False whether the cameras were taken from the plotwatcher pro camera series (recommended), which need a specific parameter set.
Adapt:
HitRate:
Minimum sensitivity:

Source Installation 
---------------

1. Download anaconda distribution of python which includes a number of scientific modules:  https://store.continuum.io/cshop/anaconda/

or 

1. Download and install python 2.7
2. Download and install numpy and scipy
3. OpenCV (tested on 2.4.9): http://opencv.org/downloads.html
4. Copy the python bindings! see: http://stackoverflow.com/questions/4709301/installing-opencv-on-windows-7-for-python-2-7 and other SOF questions on this detail.
	* Extract OpenCV (will be extracted to a folder opencv)
	* Copy ..\opencv\build\python\x86\2.7\cv2.pyd
	* Paste it in C:\Python27\Lib\site-packages
5. Confirm opencv connection by opening Python IDLE or terminal, and type "import cv2", if you recieve no errors, everything is connected
6. Install FFmpeg for capturing videos
	* FFmpeg needs to be installed and connected in the path folder: http://www.ffmpeg.org/download.html - this allows access to a wide variety of system codecs.
	* Copy everything in C:\OpenCV\3rdparty\ffmpeg\ to C:\Python27\ and rename opencv_ffmpeg.dll to opencv_ffmpeg249.dll or whatever your version of opencv (eg. OpenCV2.4.9 would be opencv_ffmpeg249.dll) 
	* If you have a problem post it: http://stackoverflow.com/questions/11699298/opencv-2-4-videocapture-not-working-on-windows/24120579#24120579, 
*Make sure to run the following checks:*

FFmpeg is exported and in the path variables, typing ffmpeg into cmd prompt will boot the program Python path is exported, calling python from cmd boots the program The #!shebang in the top of the motion.py script matches the location of python (type 'where python' into cmd to check directory location)


Note: *Please check paths depending on your cloned git library - they may not be relative in all cases.*
