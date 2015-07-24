#Script takes one argument, which is where the bin should be made.

#Install opencv and ffmpeg on bisque iplant rogers server
#Ben Weinstein - 7/24/2015

#Following here
#install dependencies
sudo yum install gtk2-devel libdc1394-devel libv4l-devel install ffmpeg-devel install gstreamer-plugins-base-devel libjpeg-turbo-devel jasper-devel openexr-devel libpng-devel libtiff-devel libwebp-devel

sudo yum install tbb-devel

#clone opencv
git clone https://github.com/Itseez/opencv.git

#build a folder
mkdir build
cd build

cmake -D WITH_TBB=ON -D WITH_EIGEN=ON ..

cmake -D BUILD_DOCS=ON -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF ..

#Disable GNU
cmake -D WITH_OPENCL=OFF -D WITH_CUDA=OFF -D BUILD_opencv_gpu=OFF -D BUILD_opencv_gpuarithm=OFF -D BUILD_opencv_gpubgsegm=OFF -D BUILD_opencv_gpucodec=OFF -D BUILD_opencv_gpufeatures2d=OFF -D BUILD_opencv_gpufilters=OFF -D BUILD_opencv_gpuimgproc=OFF -D BUILD_opencv_gpulegacy=OFF -D BUILD_opencv_gpuoptflow=OFF -D BUILD_opencv_gpustereo=OFF -D BUILD_opencv_gpuwarping=OFF ..

#where to install it?
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX= "$1" ..

make

sudo make install

#transfer libraries

su mv cat "$1"/lib/python2.6/site-packages/cv2.so "$1"/lib/python2.6/site-packages

#run a test

python

import cv2

exit()

#test file

cd /home/bw4sz/bisque/engine/modules/motionmeerkat/MotionMeerkat

./main.py --i PlotwatcherTest.avi
