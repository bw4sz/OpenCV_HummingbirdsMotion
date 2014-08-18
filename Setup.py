from distutils.core import setup
import py2exe
import sys

sys.argv.append('py2exe')

setup(
    console=['motion_dev.py'],
    data_files=[('', ['testing/PlotwatcherTest.TLV',"Bisque_DEV/public/thumbnail.ico","C:\Python27\opencv_ffmpeg249.dll","C:\Python27\Lib\site-packages\shapely\DLLs\geos.dll"])],
    options = {"py2exe":{
        'packages':['shapely'],
        "dll_excludes": ["MSVCP90.dll"]
    }}    
)

