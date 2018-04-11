#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation 
import numpy as np

import ipywidgets as widgets
from ipywidgets import interact
from IPython.display import display

import time

#import RPi.GPIO as gpio

class MyLab:
    
    OO_dummy = {}
    light = True
        
    def LabControls(self,devices,light):
        self.light = light
        Controls = self.DeviceControls(devices,self.OO_dummy);
        
    def LabControls_show(self):
        interact(self.LabControls, devices = widgets.RadioButtons(
                        options=[key for key in self.OO_dummy.keys()]), 
                                 light = True);
        
    class DeviceControls():
        def __init__(self, devices, device_dict):
            self.device = device_dict[devices]
            style = {'description_width': 'initial'}
            interact(self.actions, 
                     IT = widgets.BoundedIntText(value = 15,min=15,max = 500, 
                                         description='Integration time [ms]', style=style),
                     ElectricDarkCorrection = False)
            
        def actions(self, IT, ElectricDarkCorrection):
            self.device.IT = IT
            self.device.ElectricDarkCorrection = ElectricDarkCorrection
            
    def show_DataFeed(self):
        controls = [MyLab.OO_dummy[device].stream.play for device in [key for key in self.OO_dummy.keys()]]
        display(widgets.Box(controls))
        plt.show()        

    class Device:
        IT = 15
        ElectricDarkCorrection = False
        x = [i+200 for i in range(700)]
        stream = None
                
        def __init__(self, parent):
            self.parent = parent
           
        def close(self):
            print('device closed')

        def start_stream(self, ViewPort, turn):
            if not self.stream:
                self.stream = self.parent.LiveFeed(self, ViewPort, turn)
                self.stream.start()
            else:
                pass

        def gaussian(self, wl, mu, sig):
            wl = np.array(wl)
            return np.exp(-np.power(wl - mu, 2.) / (2 * np.power(sig, 2.)))

        def signal(self):
            
            if not self.ElectricDarkCorrection:
                ElectricDark = 1900
            else:
                ElectricDark=0
                
            time.sleep(self.IT/1000)
            if self.parent.light:
                y = [ElectricDark+100*np.random.random() for i in range(700)]+self.IT*500*(
                    self.gaussian(self.x, 450, 15)+self.gaussian(self.x, 600, 80))
                y[y>65000] = 65000
                return y
            else:
                y = [1900+100*np.random.random()*self.IT for i in range(700)]
                return y

        def capture(self):
            if not self.stream:
                pass
            else:
                self.stream.pause()
                signal = self.signal()
                I = {'mean_spec':signal, 'std_dev':np.array([]), 'N':1, 'IT':self.IT}
                time.sleep(self.IT/1000)
                print('data accessed')
                self.stream.pause()
                return I

    class LiveFeed():

        def __init__(self, device, viewport, slot):
            self.device = device
            self.parent = self.device.parent
            
            self.fig = viewport
            self.ax = slot
            #self.pos = position
            self.streaming = True

            # define and add buttons for interaction
            self.play = widgets.Button(description=self.device.name,disabled=False,
                                        button_style='', # 'success', 'info', 'warning', 'danger' or ''
                                        tooltip='Pause/Resume', 
                                        icon='pause')
            #display(self.play)
            self.play.on_click(self.interrupt)

            # create the plot
            self.plot, = self.ax.plot(self.device.x, self.device.signal(), 'o', ms=1)
            self.ax.set_ylabel('Intensity/counts')
            self.ax.set_xlabel('Wavelength/nm')

            # get initial spectral data
            self.data = (self.device.x,self.device.signal())
            self.animate = FuncAnimation(self.fig, self.update)


        def close(self):
            self.interrupt()
            self.device.close()
                    
        def start(self):
            self.animate
            
            
        def update(self, i): 
            
            if self.streaming:
                self.plot.set_data(self.device.x, self.device.signal())            
                self.plot.set_label(self.device.name+' | Integration time: '+str(self.device.IT)+' ms')
                self.ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, mode="expand", borderaxespad=0.)
                self.ax.relim()
                self.ax.autoscale_view(True,True,True)
                return self.plot
            else:
                pass
    
        def interrupt(self, b):   
            self.streaming = not self.streaming
            if not self.streaming:
                self.play.icon = 'play'
            else:
                self.play.icon = 'pause'
        
        def pause(self):
            self.streaming = not self.streaming
            if not self.streaming:
                self.play.icon = 'play'
            else:
                self.play.icon = 'pause'
                    
    def monitor(self):
        port = plt.figure()
        def up(i):
            next_plot=port.plot(i, i)
            status = print(i)
            return status,next_plot
        self.monitoring = FuncAnimation(port, up)  
        #plt.show()
        
# =======================================================
if __name__=="__main__":
    
    import getpass
    user = getpass.getuser()  
     
    MyLab = MyLab()
    MyLab.devices=['QEPro']
    #MyLab.devices=['QEPro']
    print('\n Hello '+ user + '! Welcome to MyOpticsLab (dummy version)')  
    print('\n The following Ocean Optics devices are being simulated.')
    
    ViewPort = plt.figure('Live Data Feed')
    spec_count = len(MyLab.devices)
    if spec_count == 1:
        slots = [ViewPort.subplots(spec_count, sharex=True, sharey=True)]
    else:
        slots = ViewPort.subplots(spec_count, sharex=True, sharey=True)
        
    for i,dev in enumerate(MyLab.devices):
        MyLab.OO_dummy[dev] = MyLab.Device(MyLab)
        MyLab.OO_dummy[dev].name = dev
        MyLab.OO_dummy[dev].start_stream(ViewPort,slots[i])
    #plt.show()
    MyLab.LabControls_show()
