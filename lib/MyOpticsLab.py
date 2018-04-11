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
    
    using_TTLshutter = False

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
        
        def __init__(self, device, viewport, slot):
            
            self.device = device
            self.parent = self.device.parent
            
            # initiate Figure for data visualisation
            self.fig = viewport
            self.ax = slot
            self.streaming = True

            # define and add buttons for interaction
            self.play = widgets.Button(description=self.device.name,disabled=False,
                                        button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                        tooltip='Pause/Resume', 
                                        icon='pause')            
            self.play.on_click(self.interrupt)
            
            # get initial spectral data
            self.data = self.device.get_spectrum()
            
            # create the plot
            self.plot, = self.ax.plot(self.data[0], self.data[1], 'o', ms=1)
            self.ax.set_ylabel('Intensity/counts')
            self.ax.set_xlabel('Wavelength/nm')
            
            # update the plot using Animation
            self.animate = FuncAnimation(self.fig, self.update)
        
        def start(self):
            self.animate
            
            
        def close(self):
        
            self.interrupt()
            self.device.close()
        
        def interrupt(self):   
            
            self.streaming = not self.streaming
            if not self.streaming:
                self.play.icon = 'play'
            else:
                self.play.icon = 'pause'
           
        
        def update(self, i): 
            
            if self.streaming:
                self.plot.set_data(self.data[0], self.device.get_signal())            
                self.plot.set_label(self.device.name+' | Integration time: '+str(self.device.IT/1000)+' ms')
                self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, mode="expand", borderaxespad=0.)
                self.ax.relim()
                self.ax.autoscale_view(True,True,True)
                return self.plot
            else:
                pass
            


# =============================================================================
# Some functions for iPython widgets
# =============================================================================
    def LabControls(self,devices,light):
        if light:
            OO[devices].light_on()
        else:
            OO[devices].light_off()
                
        Controls = self.DeviceControls(devices, OO);
        
    def LabControls_show(self):
        interact(self.LabControls, devices = widgets.RadioButtons(
                        options=[key for key in OO.keys()]), 
                                 light = False);
        
    class DeviceControls():
        def __init__(self, devices, device_dict):
            self.device = device_dict[devices]
            style = {'description_width': 'initial'}
            interact(self.actions, 
                     IT = widgets.BoundedIntText(value = 15,min=15,max = 500, 
                                         description='Integration time [ms]', style=style),
                     ElectricDarkCorrection = False)
            
        def actions(self, IT, ElectricDarkCorrection):
            self.device.set_IT(IT)
            self.DarkCurrentCorrect = ElectricDarkCorrection
    
    def show_DataFeed(self):
        controls = [OO[device].stream.play for device in [key for key in OO.keys()]]
        display(widgets.Box(controls))
        plt.show()      
            
# =============================================================================
# Prior Animation creating Absorbance plots
# =============================================================================

    def anim_I(self, i):
                   
        sp.set_IT(MyLab.IT)
        #self.ax = fig.add_subplot(2,2,locate)
        WL_array = sp.WL
        
        if self.i0 == 'undefined':
            Intensities = sp.avg_spec(self.n_avg)['mean spec']
        else:
            Intensities = sp.avg_spec(self.n_avg)['mean spec']-self.i0['dark']
            
        self.Graphic_Livefeed.axes[0].clear()        
        self.Graphic_Livefeed.axes[0].set_title('Intensity')
        self.Graphic_Livefeed.n_plots = [0 for n in range(2)]
        self.Graphic_Livefeed.line('$I$', WL_array, Intensities, subplot=0)
    
    def anim_A(self, i):
        
        if self.i0 == 'undefined':
            pass
        else:
    
            #self.ax = fig.add_subplot(2,2,locate)
            WL_array = sp.WL
            i = sp.avg_spec(self.n_avg)
            Intensities = (
                i['mean spec']/i['IT']*1000)-self.i0['dark']/self.i0['IT']*1000
            Reference = self.i0['mean spec']/self.i0['IT']*1000
            Absorbance = MyFuncs.Absorbance(Intensities, Reference)
            
            self.Graphic_Livefeed.axes[1].clear()
            self.Graphic_Livefeed.axes[1].set_title('Absorbance')
            self.Graphic_Livefeed.axes[1].set_ylim(self.ylims)
            self.Graphic_Livefeed.line('$A$',WL_array, Absorbance, subplot=1)
        

    def AbsorbanceAnimation(self):
        
        self.Graphic_Livefeed = MyFigure(['Intensity', 'Absorbance'], 2)
        self.Graphic_Livefeed.fig.suptitle('Live data feed')        
        I_live = animation.FuncAnimation(self.Graphic_Livefeed.fig, self.anim_I, 
                                       interval = 1000)
        A_live = animation.FuncAnimation(self.Graphic_Livefeed.fig, self.anim_A, 
                                       interval = 1000)
#        plt.show()
        
        return I_live, A_live
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
              
# =============================================================================
# Init all
# =============================================================================

if __name__=="__main__":

    import os as os
    
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation 
    
    import numpy as np
    
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
        MyLab.NonlinCorrect = False
        MyLab.DarkCurrentCorrect = False
        OO = {}
        # Create ViewPort for live plot of intensities
        ViewPort = plt.figure('Live Data Feed', figsize=(8,6))
        spec_count = len(MyLab.devices)
        if spec_count == 1:
            slots = [ViewPort.subplots(spec_count, sharex=True, sharey=True)]
        else:
            slots = ViewPort.subplots(spec_count, sharex=True, sharey=True)

        for i,device in enumerate(MyLab.devices):
            # Create a Seabreeze instance
            OO[MyLab.SeaBreeze_dict[str(device)]] = MySpectrometer(sb, sbs, MyLab, device)
            OO[MyLab.SeaBreeze_dict[str(device)]].name = MyLab.SeaBreeze_dict[str(device)]
            OO[MyLab.SeaBreeze_dict[str(device)]].set_IT(MyLab.IT)
            print('\n Connected to',MyLab.SeaBreeze_dict[str(device)])
            # Start corresponding data Live Feed
            OO[MyLab.SeaBreeze_dict[str(device)]].start_stream(ViewPort, slots[i])
        MyLab.LabControls_show()

    else:
        print('\n No Ocean Optics devices connected.')


