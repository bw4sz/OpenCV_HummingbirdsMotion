from distutils.core import setup
import py2exe
import sys
import numpy 
sys.argv.append('py2exe')

setup(
    console=['main.py'],
    data_files=[('', ["C:\Python27\opencv_ffmpeg300.dll","C:\Python27\Lib\site-packages\shapely\DLLs\geos.dll","C:\Users\Ben\Documents\OpenCV_HummingbirdsMotion\PlotwatcherTest.tlv"])],
    options = {"py2exe":{
        'packages':['shapely'],
        'includes':['numpy'],
        "dll_excludes": ["MSVCP90.dll","libzmq.pyd"]
    }}    
)

