#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper function for repeating a function with a period and storing data in hdf5 format.

Created on Fri Apr 13 2018

@author: tobiasnils

"""
class CamBasics():
    cv2 = __import__('cv2') 
    mpl = __import__('matplotlib.pyplot')
    plt=mpl.pyplot
    # A status button and progressbar is displayed to indicate the state of the loop
    widgets = __import__('ipywidgets')
    interact = widgets.interact
    ipyd = __import__('IPython.display')
    display = ipyd.display.display
    
    def __init__(self):
        
        self.device_id = 1
        self.device = self.cv2.VideoCapture(self.device_id)
        d,f,g = self.cv2.split(self.device.read()[1])
        pic = self.cv2.merge([g,f,d])
        self.plt.imshow(pic)
        self.plt.show()
        self.record = self.widgets.Button(description='current view',button_style = '', icon='play')
        self.record.on_click(self.view)
        self.save = self.widgets.Button(description='save image',button_style = '', icon='save')
        self.save.on_click(self.save_image)
        
        self.controls = self.widgets.HBox([self.record, self.save])
        
        self.widgets.interact(self.set_video, video=self.widgets.BoundedIntText(value=1,min=0,max=2, description='device index',disabled=False)); 
        self.show_controls()
            
    def set_video(self, video):
        self.device = self.cv2.VideoCapture(video) 
    def view(self, b):
        bgr_pic = [self.device.read()[1] for i in range(7)][-1]
        blue,green,red = self.cv2.split(bgr_pic)
        rgb_pic = self.cv2.merge([red,green,blue])
        self.plt.imshow(rgb_pic)
        self.plt.show()
        
    def save_image(self, b):
        bgr_pic = [self.device.read() for i in range(7)][-1]
        save_to= input('specify "folder/filename": ')
        self.cv2.imwrite(save_to+'.png', bgr_pic)
    
    def show_controls(self):
        self.display(self.controls);
        
    def record_many(self, device, period_minutes = .05, save_to = None):

        import numpy as np
        import cv2       
        # initial time t0:
        import time
        t0 = time.time()

        # Setup saving
        if save_to:
            save_to = save_to+'/'
        else:
            pass

        status = self.widgets.Button(description='Running',button_style = 'success', disabled=True)
        progress = self.widgets.FloatProgress(
                    value=0, min=0.0, max=100.0, step=0.01,
                    description='Time to next readout:',
                    bar_style='info',
                    style = {'description_width': 'initial'},
                    orientation='horizontal'
                )
        self.display(self.widgets.Box([status,progress]))

        # "Stop" defaults to False to get the loop running initially
        np.save('stop', False)

        # the repetition is initiated indefinitely unless "stop.npy" is altered accordingly by another python instance
        while True:    
            stop = np.load('stop.npy').item()
            if stop == False:
                # determine current elapsed time t in minutes
                t = round((time.time()-t0)/60, 2)

                # adjust status button appearance
                appearance = ['Running', 'info']
                status.description = appearance[0]
                status.button_style = appearance[1]        
                np.save('status', appearance)

                # acquire picture(s)
                pic = [self.device.read() for i in range(10)][-1]
                # save the last picture            
                save_name = '%s_minutes' % t
                self.cv2.imwrite(save_to+save_name+'.png', pic[1])            

                # sleep for the specified period of time [min]
                partial = period_minutes*60/100
                for j in range(100):
                    time.sleep(partial)
                    progress.value = 100-j
                    np.save('progress', 100-j)

            elif stop == True:

                # adjust status appearance
                appearance = ['Paused', 'danger']
                status.description = appearance[0]
                status.button_style = appearance[1]  
                np.save('status', appearance)

               # sleep during a time to avoid unnecessary loop repitions during pause cycles 
                # while providing sufficient reactiveness of the script
                time.sleep(.25)

            else:
                # adjust status button appearance
                appearance = ['Finished: Experiment ended by user.', '']
                status.description = appearance[0]
                status.button_style = appearance[1]
                np.save('status', appearance)

                break



def repeat_cam(device, period_minutes = .05, save_to = None):

    import numpy as np
    import cv2       
    # initial time t0:
    import time
    t0 = time.time()
    
    # Setup saving
    if save_to:
        save_to = save_to+'/'
    else:
        pass
      
    # A status button and progressbar is displayed to indicate the state of the loop
    import ipywidgets as widgets
    from ipywidgets import interact
    from IPython.display import display

    status = widgets.Button(description='Running',button_style = 'success', disabled=True)
    progress = widgets.FloatProgress(
                value=0, min=0.0, max=100.0, step=0.01,
                description='Time to next readout:',
                bar_style='info',
                style = {'description_width': 'initial'},
                orientation='horizontal'
            )
    display(widgets.Box([status,progress]))
    
    # "Stop" defaults to False to get the loop running initially
    np.save('stop', False)
    
    # the repetition is initiated indefinitely unless "stop.npy" is altered accordingly by another python instance
    while True:    
        stop = np.load('stop.npy').item()
        if stop == False:
            # determine current elapsed time t in minutes
            t = round((time.time()-t0)/60, 2)
            
            # adjust status button appearance
            appearance = ['Running', 'info']
            status.description = appearance[0]
            status.button_style = appearance[1]        
            np.save('status', appearance)
            
            # acquire picture(s)
            pic = [device.read() for i in range(10)][-1]
            # save the last picture            
            save_name = '%s_minutes' % t
            cv2.imwrite(save_to+save_name+'.png', pic[1])            
            
            # sleep for the specified period of time [min]
            partial = period_minutes*60/100
            for j in range(100):
                time.sleep(partial)
                progress.value = 100-j
                np.save('progress', 100-j)
            
        elif stop == True:
                        
            # adjust status appearance
            appearance = ['Paused', 'danger']
            status.description = appearance[0]
            status.button_style = appearance[1]  
            np.save('status', appearance)
            
           # sleep during a time to avoid unnecessary loop repitions during pause cycles 
            # while providing sufficient reactiveness of the script
            time.sleep(.25)
            
        else:
            # adjust status button appearance
            appearance = ['Finished: Experiment ended by user.', '']
            status.description = appearance[0]
            status.button_style = appearance[1]
            np.save('status', appearance)
            
            break
