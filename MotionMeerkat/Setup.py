from distutils.core import setup
import py2exe
import sys
import numpy 
import numpy.core
import numpy.core.multiarray
import shapely
import glob

sys.argv.append('py2exe')

#ignore all of the old windows modules

setup(
    console=['main.py'],
    data_files=[('', ["C:\Python27\opencv_ffmpeg310.dll","C:\Python27\Lib\site-packages\shapely\DLLs\geos_c.dll","C:\Users\Ben\Documents\OpenCV_HummingbirdsMotion\PlotwatcherTest.tlv"])],
    options = {"py2exe":{
        'bundle_files':1,
        'packages':['shapely'],
        'includes':['numpy'],
        "dll_excludes": ["libzmq.pyd","geos_c.dll","api-ms-win-core-string-l1-1-0.dll","api-ms-win-core-registry-l1-1-0.dll","api-ms-win-core-errorhandling-l1-1-1.dll","api-ms-win-core-string-l2-1-0.dll","api-ms-win-core-profile-l1-1-0.dll","api-ms-win*.dll","api-ms-win-core-processthreads-l1-1-2.dll","api-ms-win-core-libraryloader-l1-2-1.dll","api-ms-win-core-file-l1-2-1.dll","api-ms-win-security-base-l1-2-0.dll","api-ms-win-eventing-provider-l1-1-0.dll","api-ms-win-core-heap-l2-1-0.dll","api-ms-win-core-libraryloader-l1-2-0.dll","api-ms-win-core-localization-l1-2-1.dll","api-ms-win-core-sysinfo-l1-2-1.dll","api-ms-win-core-synch-l1-2-0.dll","api-ms-win-core-heap-l1-2-0.dll","api-ms-win-core-handle-l1-1-0.dll","api-ms-win-core-io-l1-1-1.dll","api-ms-win-core-com-l1-1-1.dll","api-ms-win-core-memory-l1-1-2.dll","api-ms-win-core-version-l1-1-1.dll","api-ms-win-core-version-l1-1-0.dll"]
    }}    
)

