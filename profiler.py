import pstats
import os
import cProfile

os.system("python -m cProfile -o C:/MotionMeerkat/profile.txt C:/Users/Ben/Documents/OpenCV_HummingbirdsMotion/MotionMeerkat/main.py  --set_ROI --ROI=exclude --subMethod=MOG --inDEST="C:\Users\Ben\Dropbox\MotionDetection_BetaData\Santana-Garcon\garcon_test.avi" --fileD="C:/Users/Ben/Desktop/MotionMeerkatTest/"")
p = pstats.Stats('C:/MotionMeerkat/profile.txt')
p.sort_stats('cumulative').print_stats(20)

#To call total time, in case you want to compare
p.total_tt

