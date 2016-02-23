import matplotlib.pyplot as plt
import numpy as np

def minsizeplot(array):
    plt.plot(array)
    plt.ylabel("Avg Size of Motion Objects\n(% of Frame)")
    
def returnplots(array):
    x=range(0,len(array))
    plt.step(x=x,y=array)
    plt.ylim(-.1,1.1)
    plt.yticks([0,1],['Discarded','Returned'],rotation='vertical')
    plt.xlabel("Frame")

def combineplots(minsize,returnframes):
    plt.figure(1)
    plt.subplot(2,1,1)    
    plt.title("Diagnostics")    
    minsizeplot(minsize)
    
    plt.subplot(2,1,2)
    returnplots(returnframes)
    plt.show()
    