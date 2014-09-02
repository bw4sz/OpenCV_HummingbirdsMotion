import pstats
import os
import cProfile

os.system("python -m cProfile -o C:/MotionMeerkat/profile.txt C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/motion_dev.py --threshT=60 --set_ROI --ROI_include=exclude --i C:\Users\Ben\Downloads\exampleMB.mp4")
p = pstats.Stats('C:/MotionMeerkat/profile.txt')
p.sort_stats('cumulative').print_stats(20)

#To call total time, in case you want to compare
p.total_tt

