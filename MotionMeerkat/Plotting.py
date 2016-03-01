import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.lines as mlines
import numpy as np

def minsizeplot(array,mincontour) :
    plt.plot(array)
    plt.ylabel("Max Size of Motion Objects\n(% of Frame)")
    plt.axhline(y=mincontour,color='r',ls='dashed')
    plt.ylim(0,max([max(array),mincontour+0.001]))
    
    
def returnplots(array):
    x=range(0,len(array))
    plt.step(x=x,y=array)
    plt.ylim(-.1,1.1)
    plt.yticks([0,1],['Discarded','Returned'],rotation='vertical')
    plt.xlabel("Frame")

def combineplots(minsize,returnframes,mincontour,fname,show):
    
    try:
        #clear any previous plots
        plt.clf()
        plt.cla()
        
        plt.figure(1)
        #Top Plot
        ax=plt.subplot(2,1,1)    
        plt.title("Diagnostics")    
        minsizeplot(minsize,mincontour)
        
        # add legend
        red_line = mlines.Line2D([], [], color='red', ls='dashed', label='Minimum size set by user')
        plt.legend(handles=[red_line],bbox_to_anchor=(1, 1),
                   bbox_transform=plt.gcf().transFigure,prop={'size':9})    
        
        #Format percentages axis
        fmt = '%.2f%%' # Format you want the ticks, e.g. '40%'
        yticks = mtick.FormatStrFormatter(fmt)
        ax.yaxis.set_major_formatter(yticks)     

        #Bottom Plot
        plt.subplot(2,1,2)
        returnplots(returnframes)
        plt.tight_layout()    
        plt.savefig(fname)        
        if show:
            plt.show()        
    except:
        print("Windows version < 10 may have trouble showing diagnostic plots. Plots were skipped.")
    