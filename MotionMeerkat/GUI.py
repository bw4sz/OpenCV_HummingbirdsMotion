from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock

#Screen manager
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

#For hyperlinks
import webbrowser

#MotionMeerkat
import motionClass
import arguments
import wrapper
import Plotting

#temp
from time import sleep

class MainScreen(Screen):
         
     #The behavior of these defaults are then overridden by user interaction.
     
     def help_site(instance):
          webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki")
        
     def help_issue(instance):
          webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/issues")
     
     def on_check_roi(self, value,motionVid):
          if value:
               motionVid.set_ROI=True
          else:
               motionVid.set_ROI=False
     
     #Drawing checkbox
     def on_check_draw(self, value,motionVid):     
          if value:
               motionVid.drawSmall='draw'
          else:
               motionVid.drawSmall='enter'
     
     def run_press(self,root):
          root.getProgress()
     
     def gotoAdvanced(self,screenmanage):
          name='A'
          s=AdvancedScreen(name=name)
          screenmanage.add_widget(s)
          screenmanage.current='A'
          
class AdvancedScreen(Screen):
     def gotoMain(self,screenmanage):
          screenmanage.transition.direction='right'          
          screenmanage.current='GUI'   
          
class ProgressScreen(Screen):     
     def MotionM(self,motionVid):
          arguments.arguments(motionVid)
          motionVid.wrap()
          self.ids.pb.value=75
          sleep(1)
          self.ids.pb.value=100
          print(motionVid.frame_count)
          
     def gotoresults(self,screenmanage):
          screenmanage.transition.direction='right'                   
          name='R'
          s=ResultsScreen(name=name)
          screenmanage.add_widget(s)
          screenmanage.current='R'        

class ResultsScreen(Screen):
          
     def gotoMain(self,screenmanage):
          screenmanage.transition.direction='left'          
          screenmanage.current='GUI'    
     #generate plots
     def plots(self,motionVid):
          Plotting.combineplots(motionVid.scale_size,motionVid.frame_results,motionVid.minSIZE/100,motionVid.file_destination + "/" + "Diagnostics.png",show=True)


class MyScreenManager(ScreenManager):
    
     #Create motion instance class
     motionVid=motionClass.Motion()
     
     #Initialize properties
     #def __init__(self,**kwargs):
      #    motionVid.mode=
     
     #set defaults by auto mode, could be done clear through kivy properties
     motionVid.mode='auto'
     motionVid.inDEST="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv"
     motionVid.fileD="C:/MotionMeerkat"
     motionVid.q1=3
     motionVid.q2=3
     motionVid.drawSmall='enter'
     motionVid.minSIZE=0.03
     motionVid.set_ROI=False

     def getProgress(self):
          name='P'
          s=ProgressScreen(name=name)
          self.add_widget(s)
          self.current='P'

class MotionMeerkatApp(App):
     def build(self):
          return MyScreenManager()
       
if __name__ == "__main__":
     MotionMeerkatApp().run()

