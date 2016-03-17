def GUI():
    from kivy.logger import Logger    
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
            
    class MotionMeerkatApp(App):
        def build(self):
            
            #Defaults for input variables
            self.mode='auto'
            self.set_ROI=False
            self.mogl=3
            self.mogv=3
            self.drawSmall='enter'
            
            #create overall layout
            b = BoxLayout(orientation='vertical',spacing=0)
            
            #MotionMeerkat
            top = BoxLayout(orientation='vertical',spacing=-1,size_hint=(.25,1))
            t1=Label(text="MotionMeerkat V2.0",font_size=12)
            t2=Button(text="Help",font_size=10)
            
            def help_site(instance):
                webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/wiki")
            t2.bind(on_press=help_site)
            
            t3=Button(text="Submit Issue",font_size=10)
            def help_site(instance):
                webbrowser.open("https://github.com/bw4sz/OpenCV_HummingbirdsMotion/issues")
            t3.bind(on_press=help_site)        
            top.add_widget(t1)
            top.add_widget(t2)
            top.add_widget(t3)
    
            #Input file
            #########################
            #send to manual mode on press.
            def mm_callback(instance):
                self.mode='manual'
                self.exit()
                
            self.fc=TextInput(text="Input File or Folder",font_size=20,size_hint=(1,.5))
            self.outd=TextInput(text="Output Location (C:/MotionMeerktat)",font_size=20,size_hint=(.645,.5),pos_hint={'center_x':0.485})
            
            mm=Button(text="Go to manual mode",size_hint=(.3,.5),on_press=mm_callback)
    
            banner = BoxLayout(orientation='horizontal',size_hint=(1,1))
            banner.add_widget(top)
            banner.add_widget(self.fc)
            banner.add_widget(mm)
            
            #add banner to overall 
            b.add_widget(banner)
            b.add_widget(self.outd)
            
            #########################
            ####Mog sensitivity slider
            #########################
            
            #layout
            mogbox = BoxLayout(orientation='horizontal',spacing=10,size_hint=(1,.2),pos_hint={'center_x':0.5})
        
            #actions
            moglabel=Label(text="How much background variation [eg. wind, waves, debris] do you expect in your video?",font_size=15,size_hint=(1,1))
            moglearn = Slider(min=0, max=5, value=3,size_hint=(.7,1),step=1)
            
            #define high
            moglow=Label(text="No Movement",font_size=15,size_hint=(.15,1))
    
            #define low
            moghigh=Label(text="Extreme movement",font_size=15,size_hint=(.15,1))
            
            #Define output
            mogout=Label(font_size=20,size_hint=(.1,1))
            
            def on_call(instance, value):
                mogout.text = str(int(moglearn.value))
                
            moglearn.bind(value=on_call)
            
            #add to overall layout
            b.add_widget(moglabel)
            b.add_widget(mogbox)  
            
            #add slider and labels to sublayout
            mogbox.add_widget(moglow)
            mogbox.add_widget(moglearn)
            mogbox.add_widget(moghigh)
            mogbox.add_widget(mogout)
            
            #######################
            #Tolerance slider
            #######################
            
            tolbox = BoxLayout(orientation='horizontal',spacing=10,size_hint=(1,.6),pos_hint={'center_y':0.1})
            tollabel=Label(text="How quickly does your organism move?",font_size=15,size_hint=(1,0.6))      
            tollearn = Slider(min=0, max=5, value=3,size_hint=(.7,1),step=1)
            
            #images
            cartoons=BoxLayout(size_hint=(.8,.4),pos_hint={'center_x':0.47})
            shark=Image(source="images/shark.png")
            butterfly=Image(source="images/butterfly.png")        
            Bird=Image(source="images/bird.png")        
            
            cartoons.add_widget(shark)
            cartoons.add_widget(butterfly)        
            cartoons.add_widget(Bird)
            
            #define high
            tollow=Label(text="Slow",font_size=15,size_hint=(.15,1))
    
            #define low
            tolhigh=Label(text="Fast",font_size=15,size_hint=(.15,1))
            
            #Define output
            tolout=Label(font_size=20,size_hint=(.1,1))
            
            def on_call(instance, value):
                tolout.text = str(int(tollearn.value))
                self.mogv=tolout.text
            tollearn.bind(value=on_call)
           
            #add slider and labels to sublayout
            tolbox.add_widget(tollow)
            tolbox.add_widget(tollearn)
            tolbox.add_widget(tolhigh)
            tolbox.add_widget(tolout)
            
            #add to overall layout
            b.add_widget(tollabel)
            b.add_widget(cartoons)        
            b.add_widget(tolbox)           
            
            #########################
            #Cropping checkbox
            #########################
            
            def on_check_roi(checkbox, value):
                if value:
                    self.set_ROI=True
                else:
                    self.set_ROI=False
                    
            crop = CheckBox()
            crop.bind(active=on_check_roi)        
            roil=Label(text="Crop area of motion detection?",font_size=13)
            
            crop_layout=BoxLayout(orientation='vertical',size_hint=(1,.9),pos_hint={'top':1})
            crop_layout.add_widget(roil)
            crop_layout.add_widget(crop)
            
            ####################
            #Minimum size
            ####################
            
            # Minsize enter
            ms_layout=BoxLayout(orientation='vertical',size_hint=(.5,.9),pos_hint={'top':1})
            drawl=Label(text="Minimum object size (% frame)",font_size=13)
            self.mstext=TextInput(text="0.03",size_hint=(.3,1),pos_hint={'center_x':0.5})
            
            ms_layout.add_widget(drawl)
            ms_layout.add_widget(self.mstext)
            
            #Minsize draw
            ms_draw_layout=BoxLayout(orientation='vertical',size_hint=(.5,.9),pos_hint={'top':1})
            checkl=Label(text="[b]Or [/b] Draw your object size on screen",font_size=13,markup=True)        
            
            #Drawing checkbox
            def on_check_draw(checkbox, value):
                if value:
                    self.drawSmall='draw'
                else:
                    self.drawSmall='enter'
            
            draw = CheckBox()
            draw.bind(active=on_check_draw)      
                    
            ms_draw_layout.add_widget(checkl)
            ms_draw_layout.add_widget(draw)
                    
            #Add vertical layouts side by side
            bottom=BoxLayout()
            bottom.add_widget(ms_layout)
            bottom.add_widget(ms_draw_layout)
            bottom.add_widget(crop_layout)
            
            #add to root layout
            b.add_widget(bottom)
            
            #Run!
            def run_press(instance):
                    motionVid=motionClass.Motion()
                    arguments.arguments(motionVid)   
                    wrapper.wrap(motionVid)
                    
            t = Button(text='Run',font_size=40,size_hint=(1,.6),on_press=run_press)
               
            b.add_widget(t)
            
            return b
    #run
    a=MotionMeerkatApp()
    a.run()
    return([a.mode,a.set_ROI,a.mogv,a.mogl,a.drawSmall,float(a.mstext.text),a.fc.text,a.outd])
    #set arguments
