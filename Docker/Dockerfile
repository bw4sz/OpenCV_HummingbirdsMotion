FROM ubuntu:16.04
MAINTAINER Chenna Varri

RUN apt-get update
RUN apt-get install -y build-essential apt-utils

RUN apt-get install -y cmake git libgtk2.0-dev pkg-config libavcodec-dev \
  libavformat-dev libswscale-dev
RUN  apt-get update && apt-get install -y python-dev python-numpy \
  python3 python3-pip python3-dev libtbb2 libtbb-dev \
  libjpeg-dev libjasper-dev libdc1394-22-dev \
  python-opencv libopencv-dev libav-tools python-pycurl \
  libatlas-base-dev gfortran webp qt5-default libvtk6-dev zlib1g-dev

RUN pip3 install numpy

RUN apt-get install -y python-pip
RUN pip install --upgrade pip

RUN cd ~/ &&\
    git clone https://github.com/Itseez/opencv.git &&\
    git clone https://github.com/Itseez/opencv_contrib.git &&\
    cd opencv && mkdir build && cd build && cmake  -DWITH_QT=ON -DWITH_OPENGL=ON -DFORCE_VTK=ON -DWITH_TBB=ON -DWITH_GDAL=ON -DWITH_XINE=ON -DBUILD_EXAMPLES=ON .. && \
    make -j4 && make install && ldconfig

RUN cd ~/ &&\
    git clone https://github.com/bw4sz/OpenCV_HummingbirdsMotion.git --depth 1

#install python modules
#tkinter is easier by apt-get
RUN apt-get install python-tk

RUN cd ~/OpenCV_HummingbirdsMotion/Docker &&\
    pip install -r requirements.txt

# Set the appropriate link
RUN ln /dev/null /dev/raw1394

RUN cd ~/opencv