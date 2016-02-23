import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np


def minsizeplot(array,mincontour) :
    #ax = plt.subplot(111)
    plt.plot(array)
    plt.ylabel("Avg Size of Motion Objects\n(% of Frame)")
    plt.axhline(y=mincontour,color='r',ls='dashed')
    plt.ylim(0,mincontour+0.05)
    
    #Format percentages
    #fmt = '%.0f%%' # Format you want the ticks, e.g. '40%'
    #yticks = mtick.FormatStrFormatter(fmt)
    #ax.yaxis.set_major_formatter(yticks) 
    
def returnplots(array):
    x=range(0,len(array))
    plt.step(x=x,y=array)
    plt.ylim(-.1,1.1)
    plt.yticks([0,1],['Discarded','Returned'],rotation='vertical')
    plt.xlabel("Frame")

def combineplots(minsize,returnframes,mincontour,fname):
    plt.ion()
    plt.figure(1)
    plt.subplot(2,1,1)    
    plt.title("Diagnostics")    
    minsizeplot(minsize,mincontour)
    
    plt.subplot(2,1,2)
    returnplots(returnframes)
    plt.show()
    plt.savefig(fname)
    