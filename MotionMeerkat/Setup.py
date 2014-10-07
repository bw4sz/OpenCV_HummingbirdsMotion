from distutils.core import setup
import py2exe
import sys
import numpy 
sys.argv.append('py2exe')

setup(
    console=['main.py'],
    data_files=[('', ["C:\Python27\opencv_ffmpeg300.dll","C:\Python27\Lib\site-packages\shapely\DLLs\geos.dll"])],
    options = {"py2exe":{
        'packages':['shapely'],
        "dll_excludes": ["MSVCP90.dll"]
    }}    
)

