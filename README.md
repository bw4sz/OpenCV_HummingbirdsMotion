OpenCV_HummingbirdsMotion
-----------------------------

Technical Aim: Identify which frames in a video have motion and save them to file.
Use: We have been studying hummingbird plant pollination in North Ecuador. Using innovative camera traps that record images once per second, we have developed a databank of 3.5 tb of flower videos. On average, 3-5 birds visit the flowers every 6 hours. Instead of manually reviewing the videos, we are designing software using python and open_CV to analyze the videos

If you have ideas about how to do this, i'd love feedback! Please fork and try it yourself, test files are included in this repository, as well as still frame image ("17") about the desired output

General
-------------

You need open_cv, and FFmpeg installed and connected to python. Easiest solution is install python using anaconda distribution.

All testing has been done on windows, but there is no reason to expect major difficulties on linux or mac.

Installation
---------------

For completely new users, one can install the python/open cv module using simpleCV: http://simplecv.org/

Alternatively, you can download and install the anaconda distribution of python, which includes numpy and several other modules: https://store.continuum.io/cshop/anaconda/

and then install open cv: http://opencv.org/downloads.html

make sure to copy the python bindings! see: http://stackoverflow.com/questions/4709301/installing-opencv-on-windows-7-for-python-2-7 and other SOF questions on this detail.

FFmpeg needs to be installed and connected in the path folder: http://www.ffmpeg.org/download.html - this allows access to a wide variety of system codecs.

*Make sure to run the following checks:*

FFmpeg is exported and in the path variables, typing ffmpeg into cmd prompt will boot the program Python path is exported, calling python from cmd boots the program The #!shebang in the top of the motion.py script matches the location of python (type 'where python' into cmd to check directory location)

Contents
-------------
Open_CV Hummingbird.py is the workhorse function, it takes in a video path and ID name, and prints the motion images to a directory.

SingleTest.py is a sample video that shows the steps involved and creates a gui window for each step

test.py was an assortment of test analysis to ensure the system can read and write images.

Motion.py
-----------
Python executable - can be run from shell, takes in arguments file/batch mode, file input, file destination, sensitivity parameter, True/False whether the cameras were taken from the plotwatcher pro camera series (recommended), which need a specific parameter set.

If not system arguments, they will be asked for direct input.

*Please check paths depending on your cloned git library - they are not relative.*

Task List
=============

Welcome to the OpenCV_HummingbirdsMotion wiki!

Here i'm keeping track of steps needed to get the MotionMeerkat module on to the bisque platform

To do
=========

Engine server
-------------

- [] Connect to atmosphere node
- [] General review of the flow ( xml -> runtime -> python)
- [] Initialize local instant of engine server 
    - [] Example test run using engine server
    - [] Where are error files saved?

XML
-------
1. View tags on module definition file
1. Name for the folder path for output directories?

Runtime
------
1. Confirm argument passing using positional naming

Python
----
1. Confirm opts parses statement
1. Folder directory naming
1. Can i create folders, do all modules have write permission within users folders?
