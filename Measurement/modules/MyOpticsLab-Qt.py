#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 20:30:38 2017

@author: nils

Script initializing the laboratory equipment providing functions for measuremnt and control

"""

class MyOpticsLab:
          
# =============================================================================
# Keys for currently implemented Ocean Optics devices
# =============================================================================
    SeaBreeze_dict = {'<SeaBreezeDevice USB4000:FLMT00119>':'flame', 
                      '<SeaBreezeDevice USB2000PLUS:USB2+F04041>':'USB2000plus', 
                      '<SeaBreezeDevice USB2000PLUS:USB2+H02391>':'USB2000plusXR', 
                      '<SeaBreezeDevice QE65000:QEPB0195>':'QE65Pro',
                      '<SeaBreezeDevice QE-PRO:QEP00913>':'QEPro',
                      '<SeaBreezeDevice QE65000:QEB0653>':'QE65000', 
                      '<SeaBreezeDevice HR4000:HR4C2550>':'HR4000',
                      '<SeaBreezeDevice MAYA2000:MAY11044>':'Maya'}
    OO_symlinks = {'flame':'usb4000-', 
                   'QE65Pro':'qe65000+-',
                   'QE65000':'qe65000+-',
                   'QEPro':'qepro+-',
                   'USB2000':'usb2000-',
                   'USB2000plus':'usb2000+-',
                   'USB2000plusXR':'usb2000+-',
                   'Nirquest256':'nirquest256-', 
                   'Nirquest512':'nirquest512-', 
                   'HR4000':'hr4000-',
                   'Maya':'maya2000-',
                   'MayaPro':'mayapro2000-'}  
    light_source_connects = ['USB2000plus','QE65Pro', 'QE65000', 'USB2000plus']
    
# =============================================================================
# Set some global variables for the MyOpticsLab Class
# =============================================================================                
    #open_Specs = []
    List=[]
    #import matplotlib.gridspec as gridspec
    #gs = gridspec.GridSpec(7, 7)    
    
    IT = 15
    i0 = 'undefined'
    i_dark = 'undefined'
    n_avg = 1
    ylims = (-1, 1)
    
    def __init__(self, os, sl, sbs):
        import getpass
        user = getpass.getuser()  
                
        import pprint
        pp=pprint.PrettyPrinter(indent=4)
        print('\n Hello '+ user + '! Welcome to LabOptica :)')        
        
        try:
            self.devices = sbs.list_devices()
            #pp.pprint(self.List)        
            
        except sbs.SeaBreezeError:
            print('\n Permission error: This user has insufficient rights to access Ocean Optics devices.\nInstall the required "udev" rules for this user if access is required.')           
        else: 
            print('\n The following Ocean Optics devices have been recognized:')            
            #pp.pprint(self.List)        
            pp.pprint(self.devices)  
            #print('search for Ocean Optics devices using their label, e. g. "flame" or "QE65Pro"')        
            

# =============================================================================
# Define Feedback functions
# =============================================================================
    
    class LiveFeed():
        
        def __init__(self, device):
            
            self.device = device
            self.parent = self.device.parent
            
            # define Figure and Plot for other functions
            self.viewport = self.parent.ViewPort
            slot.enableAutoRange('xy', True)
            
            self.plot = slot.plot(pen='b')
            
            #self.streaming = True  
            
            # init timer for data refresh
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update)
            self.timer.start(self.device.IT+35)
        
        def start(self):
            if self.timer.isActive():
                pass
            else:
                self.timer.start(self.device.IT+35)

        def update(self): 
            self.plot.setData(self.device.WL, self.device.get_signal())
 
        #def interrupt(self):               
        #    self.parent.streaming = not self.parent.streaming
        #    if self.parent.streaming:
        #        self.timer.stop()
        #    else:
        #        self.timer.start(self.device.IT+35)
            
        def close(self):
            #self.interrupt()         
            self.timer.stop()

# =============================================================================
# Some functions for iPython widgets
# =============================================================================
    def LabControls_show(self):
        interact(self.LabControls, devices = widgets.RadioButtons(
                        options=[key for key in OO.keys()]), 
                                 light = False);

    def LabControls(self,devices,light):
        if light:
            OO[devices].light_on()
        else:
            OO[devices].light_off()
                
        Controls = self.DeviceControls(devices, OO);
        self.play = widgets.Button(description='Show Feed',
                                   disabled=False,
                                   button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                   #tooltip='Pause/Resume', 
                                   icon='play')            
        self.play.on_click(self.play_action)
            
        
    def play_action(self, b):
        for device in OO.keys():
            OO[device].start_stream(self.ViewPort, Plots[OO[device]].name)
        self.ViewPort.show()
        

        
    class DeviceControls():
        def __init__(self, devices, device_dict):
            self.device = device_dict[devices]
            style = {'description_width': 'initial'}
            interact(self.actions, 
                     IT = widgets.BoundedIntText(value = 100,min=12,max = 60000, 
                                         description='Integration time [ms]', style=style),
                     ElectricDarkCorrection = False,
                     NonlinearityCorrection = False)
            
        def actions(self, IT, ElectricDarkCorrection, NonlinearityCorrection):
            self.device.set_IT(IT)
            self.device.DarkCurrentCorrection = ElectricDarkCorrection
            self.device.NonlinearityCorrection = NonlinearityCorrection    
            
# =============================================================================
# 
# =============================================================================
    
    def Axes_init(self):
    #def Stage_init(self, Port):
        #self.Stage.connect(Port)
        #self.Stage.user_init()
        self.Axis1 = MyAxis('1', self.Stage)
        self.Axis2 = MyAxis('2', self.Stage)
        self.Axis3 = MyAxis('3', self.Stage)            
        if self.Stage.isOpen():        
            print('\n Connection to Stage successfully established')
            
# =============================================================================
# 
# =============================================================================
            
    def Cam(self, os, number_as_string):
        command = 'gnome-terminal -e \"sudo xawtv -gl -xv -vm -device /dev/video%s"' % (number_as_string)
        
        os.system(command)

        
##	Class CustomGraphicsWindow
#	We use this class to override the closeEvent function of the base pg.GraphicsWindow
class CustomGraphicsWindow(pg.GraphicsWindow):
    ##	Function closeEvent
    #	This overrides the closeEvent function in the base class. This function is invoked automatically by QTGui when the window closes.
    #	@param ev This is the event object (i.e. window close). 
    def closeEvent(self, ev):
        device.stream = None
        ev.accept()        
# =============================================================================
# Init all
# =============================================================================

if __name__=="__main__":

    import os as os
    
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation 
    
    import numpy as np
    import pyqtgraph as pg
    
    import ipywidgets as widgets
    from ipywidgets import interact
    from IPython.display import display

    # =============================================================================
    # Init Stage: Stage is deactivated as default situation
    # =============================================================================

    #import serial as sl
    #from MyStage import MyStage, MyAxis
    #MyLab.n_xips = 1
    #MyLab.Stage = MyStage(os, sl, MyLab.n_xips)
    #MyLab.Axes_init()    
    #MyLab.Stage.Axis2.step_out = [5, 5, 5]

    # =============================================================================
    # Search for and initialise Spectrometers
    # =============================================================================

    import seabreeze as sb
    sb.use('cseabreeze')
    import seabreeze.spectrometers as sbs

    ### invoke and initialize MyLabOptica instance
    MyLab = MyOpticsLab(os, sl=None, sbs=sbs)

    #import matplotlib.animation as animation

    if len(MyLab.devices) > 0:
        # Setup Spectrometers
        from MySpectrometer import MySpectrometer   
        #MyLab.NonlinCorrect = False
        #MyLab.DarkCurrentCorrect = False
        OO = {}
        # Create ViewPort for live plot of intensities
        ViewPort = CustomGraphicsWindow(title="Spectrometer LiveStream")
        ViewPort.resize(400,300)
        Plots = {}
        
        for i,device in enumerate(MyLab.devices):
            # Create a Seabreeze instance
            OO[MyLab.SeaBreeze_dict[str(device)]] = MySpectrometer(sb, sbs, MyLab, device)
            OO[MyLab.SeaBreeze_dict[str(device)]].name = MyLab.SeaBreeze_dict[str(device)]
            OO[MyLab.SeaBreeze_dict[str(device)]].set_IT(MyLab.IT)
            print('\n Connected to',MyLab.SeaBreeze_dict[str(device)])
            # Add plot to ViewPort
            Plots[MyLab.SeaBreeze_dict[str(device)]]=ViewPort.addPlot(title=MyLab.SeaBreeze_dict[str(device)],
                                         labels={'left': ('Intensity', 'counts'), 
                                                             'bottom': ('Wavelength','nm')})
            
        MyLab.LabControls_show()

    else:
        print('\n No Ocean Optics devices connected.')


