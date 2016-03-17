def GUI():
    from kivy.uix.screenmanager import ScreenManager, Screen
    
    #For hyperlinks
    import webbrowser
    
    #Main screen
    import MainScreen
    
    sm = ScreenManager()
    sm.add_widget(MainScreen())    

    class MotionMeerkatApp(App):
                
        def build(self):
            return sm
    #run
    a=MotionMeerkatApp()
    a.run()
    
