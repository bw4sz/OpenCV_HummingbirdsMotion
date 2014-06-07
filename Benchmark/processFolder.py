#!/usr/bin/python
# -*- coding: utf-8 -*-

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
#FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Nil Goyette
# University of Sherbrooke
# Sherbrooke, Quebec, Canada. April 2012

import os
import shutil
import subprocess
import sys

from Stats import Stats

call = subprocess.call

def main():    
    datasetPath = sys.argv[1]
    binaryRootPath = sys.argv[2]
    
    if not isValidRootFolder(datasetPath):
        print('The folder ' + datasetPath + ' is not a valid root folder.');
        return
    
    if os.path.exists(binaryRootPath):
        print('The folder ' + binaryRootPath + ' has been cleaned.');
        shutil.rmtree(binaryRootPath)
    os.mkdir(binaryRootPath)
    
    processFolder(datasetPath, binaryRootPath)

def processFolder(datasetPath, binaryRootPath):
    """Call your executable for all sequences in all categories."""
    #stats = Stats(datasetPath)  #STATS
    for category in getDirectories(datasetPath):
        #stats.addCategories(category)  #STATS
        
        categoryPath = os.path.join(datasetPath, category)
        os.mkdir(os.path.join(binaryRootPath, category))
        
        for video in getDirectories(categoryPath):
            videoPath = os.path.join(categoryPath, video)
            binaryPath = os.path.join(binaryRootPath, category, video)
            if isValidVideoFolder(videoPath):
                processVideoFolder(videoPath, binaryPath)            
                #confusionMatrix = compareWithGroungtruth(videoPath, binaryPath)  #STATS
                
                #stats.update(category, video, confusionMatrix)  #STATS
        #stats.writeCategoryResult(category)  #STATS
    #stats.writeOverallResults()  #STATS

def processVideoFolder(videoPath, binaryPath):
    """Call your executable on a particular sequence."""
    os.mkdir(binaryPath);
    retcode = call([os.path.join('exe', 'TODO.exe'),
                    videoPath, binaryPath],
                   shell=True)

def compareWithGroungtruth(videoPath, binaryPath):
    """Compare your binaries with the groundtruth and return the confusion matrix"""
    statFilePath = os.path.join(videoPath, 'stats.txt')
    deleteIfExists(statFilePath)

    retcode = call([os.path.join('exe', 'comparator.exe'),
                    videoPath, binaryPath],
                   shell=True)
    
    return readCMFile(statFilePath)

def readCMFile(filePath):
    """Read the file, so we can compute stats for video, category and overall."""
	if not os.path.exists(filePath):
		print("The file " + filePath + " doesn't exist.\nIt means there was an error calling the comparator.")
		raise Exception('error')
	
    with open(filePath) as f:
        for line in f.readlines():
            if line.startswith('cm:'):
                numbers = line.split()[1:]
                return [int(nb) for nb in numbers[:5]]





def isValidRootFolder(path):
    """A valid root folder must have the six categories"""
    categories = set(['dynamicBackground', 'baseline', 'cameraJitter', 'intermittentObjectMotion', 'shadow', 'thermal', 'badWeather', 'lowFramerate', 'nightVideos', 'PTZ', 'turbulence'])
    folders = set(getDirectories(path))
    return len(categories.intersection(folders)) == 6

def isValidVideoFolder(path):
    """A valid video folder must have \\groundtruth, \\input, ROI.bmp, temporalROI.txt"""
    return os.path.exists(os.path.join(path, 'groundtruth')) and os.path.exists(os.path.join(path, 'input')) and os.path.exists(os.path.join(path, 'ROI.bmp')) and os.path.exists(os.path.join(path, 'temporalROI.txt'))

def getDirectories(path):
    """Return a list of directories name on the specifed path"""
    return [file for file in os.listdir(path)
            if os.path.isdir(os.path.join(path, file))]

def deleteIfExists(path):
    if os.path.exists(path):
        os.remove(path)


if __name__ == "__main__":
    main()
