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

#For hyperlinks
import webbrowser

#MotionMeerkat
import motionClass
import arguments
import wrapper
     
class MainScreen(BoxLayout):
    
     #Create motion instance class
     motionVid=motionClass.Motion()
     
     #set defaults by auto mode, could be done clear through kivy properties
     motionVid.mode='auto'
     motionVid.inDEST="C:/Program Files (x86)/MotionMeerkat/PlotwatcherTest.tlv"
     motionVid.fileD="C:/MotionMeerkat"
     motionVid.q1=3
     motionVid.q2=3
     motionVid.drawSmall='enter'
     motionVid.minSIZE=0.03
     motionVid.set_ROI=False
     
     #The behavior of these defaults are then overridden by user interaction.
     
     def help_site(instance):
          webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki")
        
     def help_issue(instance):
          webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/issues")
     
     def on_check_roi(self, value):
          if value:
               self.set_ROI=True
          else:
               self.set_ROI=False
     
     #Drawing checkbox
     def on_check_draw(self, value):     
          if value:
               self.drawSmall=True
          else:
               self.drawSmall=False
     
     def run_press(self):
          arguments.arguments(self.motionVid)
          wrapper.wrap(self.motionVid)
          App.get_running_app().stop()
          
class MotionMeerkatApp(App):
     def build(self):
          return MainScreen()
       
if __name__ == "__main__":
     MotionMeerkatApp().run()

