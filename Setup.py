from distutils.core import setup
import py2exe
import sys

sys.argv.append('py2exe')

setup(
    console=['motion_dev.py'],
    data_files=[('data', ['testing/PlotwatcherTest.TLV'])]
)