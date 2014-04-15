OpenCV_HummingbirdsMotion
=========================

Technical Aim: Identify which frames in a video have motion and save them to file.
----------------------------------------------------------------------------------

Use: We have been studying hummingbird plant pollination in North Ecuador. Using innovative camera traps that record images once per second, we have developed a databank of 3.5 tb of flower videos.
On average, 3-5 birds visit the flowers every 6 hours. Instead of manually reviewing the videos, we are designing software using python and open_CV to analyze the videos

If you have ideas about how to do this, i'd love feedback!
Please fork and try it yourself, test files are included in this repository, as well as still frame image ("17") about the desired output

General
------------
You need open_cv, and FFmpeg installed and connected to python. Easiest solution is install python using anaconda distribution. 

Contents
----------------------
Open_CV Hummingbird.py is the workhorse function, it takes in a video path and ID name, and prints the motion images to a directory.
 
SingleTest.py is a sample video that shows the steps involved and creates a gui window for each step

test.py was an assortment of test analysis to ensure the system can read and write images. 

Motion.py
----------------

Python executable - can be run from shell, takes in three arguments file/batch mode, file input, file destination

If not system arguments, they will be asked for direct input. 

#Please check paths depending on your cloned git library - they are not relative. 
