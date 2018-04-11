#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
My custom startup file

Created on Tue Dec 13 15:06:42 2016

@author: nils
"""
import numpy as np
class MyFuncs():
        
    def Loss(i, i0):
        try:
            assert(type(i0)==np.float64 or type(i0)==np.ndarray or type(i0)==float)
            assert(type(i)==np.float64 or type(i)==np.ndarray  or type(i)==float)   
            L = -10*np.log10(i/i0)
            try:
                len(L)
                return np.array(L)
            except TypeError:    
                return float(L)
        except AssertionError:
            try:
                i, i0 = np.array(i), np.array(i0)
                L = -10*np.log10(i/i0)
                try:
                    len(L)
                    return np.array(L)
                except TypeError:    
                    return float(L)
            except:
                print('invalid input: float or array input with equal length expected')
            
    def Absorbance(i, i0):
        try:
            assert(type(i0)==np.float64 or type(i0)==np.ndarray or type(i0)==float)
            assert(type(i)==np.float64 or type(i)==np.ndarray  or type(i)==float)   
            L = -np.log10(i/i0)
            try:
                len(L)
                return np.array(L)
            except TypeError:    
                return float(L)
        except AssertionError:
            try:
                i, i0 = np.array(i), np.array(i0)
                L = -np.log10(i/i0)
                try:
                    len(L)
                    return np.array(L)
                except TypeError:    
                    return float(L)
            except:
                print('invalid input: float input expected')
                
    def load_dict(filename):
        # load dictionary in 'filename.npy' saved with np.save
        dictionary = np.load(str(filename)+'.npy').item()
        print('loaded dictionary with', dictionary.keys())
        return dictionary
    
    def fit_linear( x, y, points, fig = None):
                
        from scipy.stats import linregress
        points=points
        r_squared = 0.
        best = {}
        best['r_squared'] = r_squared
        
        for i in range(len(x)-points+1):
            
            j = points+i               
            fit=linregress(x[i:j], y[i:j])
            r_squared = fit[2]**2
                        
            if r_squared > best['r_squared']:
                best['i'] = i
                best['fit'] = fit
                best['r_squared'] = r_squared
            else:
                pass
            
        print('slope', best['fit'][0], '+/-', best['fit'][4])
        if fig==None:
            pass
        else:
            name = 'best linear fit using ' +str(points)+' points:\nslope'+ str(best['fit'][0]) + '+/-' + str(best['fit'][4])
            fig.line(name, x[best['i']:best['i']+points],[best['fit'][0]*value+best['fit'][1] for value in x[best['i']:best['i']+points]], pen='r')


#lightsources = MyFuncs.load_dict('database_lightsources')
#wl_binning = MyFuncs.load_dict('database_wl_binning')    
            
        
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
#import matplotlib.animation as animation
#from matplotlib import style

import matplotlib.cm as cm


class MyFigure(object):
    
    def __init__(self, titles, number=1,cmap='b', orientation = 'h'):
        #style.use(stil)
        self.titles = titles
        self.cmap = cmap
        if self.cmap=='b':
            self.MyMainColors = [cm.Blues_r(n*25) for n in range(10)]
            self.MySecColors = [cm.gray(n*25) for n in range(10)]
        elif self.cmap=='g':
            self.MyMainColors = [cm.gray(n*25) for n in range(10)]
            self.MySecColors = [cm.Blues_r(n*25) for n in range(10)]
        self.MyMarkers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd')
        self.n_plots = [0 for n in range(number)]
        self.n_secondary_plots = [0 for n in range(number)]
        if orientation == 'h':
            x = number*6
            y = 6
            self.fig = plt.figure(figsize=(x,y))
            self.subplots(number, orientation)

        else:
            pass
        
    def subplots(self, number, orientation):
        a = 6
        b = number*(a)+1
        self.axes = []
        if orientation == 'h':
            gs = gridspec.GridSpec(a, b)
            for n in range(number):
                if n==0:
                    self.axes.append(self.fig.add_subplot(gs[0:a,n*a:(n+1)*a]))
                    self.axes[0].set_title(self.titles[n])
                else:
                    self.axes.append(self.fig.add_subplot(gs[0:a,n*a+1:(n+1)*a+1]))
                    self.axes[n].set_title(self.titles[n])
            #self.axes[number].setlables('right')
        else:
            pass                    

    def set_xlabel(self, subplot, label):
        self.axes[subplot].set_xlabel(label)                        
    def set_ylabel(self, subplot, label):
        self.axes[subplot].set_ylabel(label)   
        
        
    def line(self, name, x, y, axis=0):
        self.axes[axis].plot(x, y, label = name, lw=1.5, alpha = .9, c = self.MyMainColors[self.n_plots[axis]])
        self.axes[axis].legend(loc='best', numpoints = 1, fontsize=9)
        self.n_plots[axis] += 1
        
        
    def scatter(self, name, x, y, axis=0):
        style = self.MyMarkers[self.n_plots[axis]]
        self.axes[axis].plot(x, y, style, label = name, lw=1.5,alpha = .9,c = self.MyMainColors[self.n_plots[axis]])
        self.axes[axis].legend(loc='best', numpoints = 1, fontsize=9)
        self.n_plots[axis] += 1
        
    def scatter_errbar(self, name, x, y, xerr=None, yerr=None, axis=0):
        style = self.MyMarkers[self.n_plots[axis]]        
        
        if not xerr==None:
            self.axes[axis].errorbar(x,y, xerr,fmt=style, mfc='none', ecolor=self.MyMainColors[self.n_plots[axis]])
        elif not yerr==None:
            self.axes[axis].errorbar(x,y, yerr,fmt=style, mfc='none', ecolor=self.MyMainColors[self.n_plots[axis]])
            
        self.axes[axis].plot(x, y, style, label = name, lw=1.5,alpha = .9,c = self.MyMainColors[self.n_plots[axis]])
        self.axes[axis].legend(loc='best', numpoints = 1, fontsize=9)
        self.n_plots[axis] += 1
           
        
    def linescatter(self, name, x, y, axis=0):
        style = self.MyMarkers[self.n_plots[axis]] + '-'
        self.axes[axis].plot(x, y, style, label = name, lw=1.5,alpha = .9, c = self.MyMainColors[self.n_plots[axis]])
        self.axes[axis].legend(loc='best', numpoints = 1, fontsize=9)
        self.n_plots[axis] += 1
        
        
    def secondary(self, name, x, y, axis=0, pen='--'):     
        self.axes[axis].plot(x, y, pen, label = name, lw=1.5,alpha = .9, c = self.MySecColors[self.n_secondary_plots[axis]])
        self.axes[axis].legend(loc='best', numpoints = 1, fontsize=9)
        self.n_secondary_plots[axis] += 1
        
    def linear_fit(self, x, y, points, pen='r-', axis=0):
        """
        from scipy.stats import linregress
        fit=linregress(x, y)
        y_fit= [fit[0]*value+fit[1] for value in x]
        name = 'linear regression:\n f(x) = '+str(round(fit[0], 5))+'*x+'+str(round(fit[1], 5))+',\nstderr='+ str(round(fit[4], 5))
        self.axes[axis].plot(x, y_fit, pen, label = name, lw=1.5,alpha = .9)
        self.axes[axis].legend(loc='best', numpoints = 1, fontsize=9)
        """
        
        from scipy.stats import linregress
        points=points
        r_squared = 0.
        best = {}
        best['r_squared'] = r_squared
        
        for i in range(len(x)-points+1):
            
            j = points+i               
            fit=linregress(x[i:j], y[i:j])
            r_squared = fit[2]**2
                        
            if r_squared > best['r_squared']:
                best['i'] = i
                best['fit'] = fit
                best['r_squared'] = r_squared
            else:
                pass
            
        print('slope', best['fit'][0], '+/-', best['fit'][4])
        self.axes[axis].plot(x[best['i']:best['i']+points],[best['fit'][0]*value+best['fit'][1] for value in x[best['i']:best['i']+points]], pen)
        
        
    def clear(self):
        for axis in self.axes:
            axis.clear()
        self.n_plots = [0 for n in range(len(self.axes))]
        self.n_secondary_plots = [0 for n in range(len(self.axes))]
        
###======================================================================================
import ipywidgets as widgets
from ipywidgets import interact
from IPython.display import display

class repeat_loop_controls():
    def __init__(self):
        self.stop = False
        np.save('stop', self.stop)
        self.button1 = widgets.Button(description='Stop/Resume')
        self.button1.on_click(self.stop_clicked)
        self.button2 = widgets.Button(description='Abort')
        self.button2.on_click(self.abort_clicked)
        
    def stop_clicked(self, b):
        self.stop = not self.stop
        np.save('stop', self.stop)
        
    def abort_clicked(self, b):
        np.save('stop', 'abort')
        
    def show(self):
        display(self.button1)
        display(self.button2)
        
###======================================================================================

def repeat_dummy(sequence, lab, period_minutes = .05, write_to = 'database', zone=None):
#def repeat(sequence, period_minutes = .05, write_to = 'database', zone=None):
       
    # initial time t0:
    import time
    try:
        t0 = np.load('times.npy')
    except FileNotFoundError:
        t0 = time.time()
        #np.save('times', np.array(t0))
    
    # datafile management with pytables and h5py defaults to 
    import tables
    db = tables.open_file(write_to+".h5", mode="a", title="Biofilm (static) Database")
    if zone==None:
        pass
    else:
        db_group = db.create_group(db.root, zone, 'Measurements at '+zone)    
    db.flush()
           
    # A status button and progressbar is displayed to indicate the state of the loop
    status = widgets.Textarea(value='',placeholder='', description='',
    disabled=False)
    progress = widgets.FloatProgress(
                value=0, min=0.0, max=100.0, step=0.01,
                description='Time to next readout:',
                bar_style='info',
                style = {'description_width': 'initial'},
                orientation='horizontal'
            )
    display(widgets.VBox([status,progress]))
    
    # "Stop" defaults to False to get the loop running initially
    np.save('stop', False)
    i=1
    # the repetition is initiated indefinitely unless "stop.npy" is altered accordingly by another python instance
    while True:    
        stop = np.load('stop.npy').item()
        if stop == False:
            # secure write access to database 
            db = tables.open_file(write_to+".h5", mode="a", title="Biofilm (static) Database")            
            
            # adjust status button appearance
            status.value = 'Running'
            status.button_style = 'info'            
           
            # define the time [s] relative to initiation of the repeat function
            #np.save('times', np.vstack((t0, np.array(time.time()))))
            t = time.time()-t0
            
            # execute the defined sequence providing t and datafile
            #I = sequence()
            I = lab.OO_dummy['QEPro'].capture()
            # add spectrum as array to database and attach attributes
            entry_name = 't%s' %i
            if zone==None:
                
                db_entry = db.create_array(db.root,entry_name, I['mean_spec'], 'Intensities at time '+str(t/3600)+' [h]')
                db_entry.attrs['time_s'] = t
                for attribute in (I.keys()-'mean_spec'):
                    db_entry.attrs[attribute] = I[attribute]   
            else:
                db_entry = db.create_array(db.root,entry_name, I['mean_spec'], 'Intensities at time '+str(t/3600)+' [h]')
                db_entry.attrs['time_s'] = t
                for attribute in I.keys():
                    db_entry.attrs[attribute] = I[attribute]   
            db.flush()
            i+=1
            # sleep for the specified period of time [min]
            partial = period_minutes*60/100
            for j in range(100):
                time.sleep(partial)
                progress.value = 100-j
            
        elif stop == True:
            # on first pass close datafile access to allow access from other python instances
            db.close()
            
            # adjust status appearance
            status.value = 'Paused'
            status.button_style = 'danger'            
            
           # sleep during a time to avoid unnecessary loop repitions during pause cycles 
            # while providing sufficient reactiveness of the script
            time.sleep(.25)
            
        else:
            # adjust status button appearance
            status.value = 'Finished: Experiment ended by user.'
            status.button_style = '' 
            # Close datafile access and end the loop for good
            db.close()
            break


###======================================================================================
def repeat(sequence, spectrometer, period_minutes = .05, write_to = 'database', zone=None):
#def repeat(sequence, period_minutes = .05, write_to = 'database', zone=None):
       
    # initial time t0:
    import time
    try:
        t0 = np.load('times.npy')
    except FileNotFoundError:
        t0 = time.time()
        #np.save('times', np.array(t0))
    
    # datafile management with pytables and h5py defaults to 
    import tables
    db = tables.open_file(write_to+".h5", mode="a", title="Biofilm (static) Database")
    if zone==None:
        pass
    else:
        db_group = db.create_group(db.root, zone, 'Measurements at '+zone)    
    
    # Create first array in database and fill it with wavelengths [nm]
    db_entry = db.create_array(db.root,'wavelength', spectrometer.WL, 'Wavelength binning provided by spectrometer')
    db_entry.attrs['Spectrometer'] = spectrometer.name
    
    db.flush()    
    
    # A status button and progressbar is displayed to indicate the state of the loop
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
    i=1
    # the repetition is initiated indefinitely unless "stop.npy" is altered accordingly by another python instance
    while True:    
        stop = np.load('stop.npy').item()
        if stop == False:
            # secure write access to database 
            db = tables.open_file(write_to+".h5", mode="a", title="Biofilm (static) Database")            
            
            # adjust status button appearance
            status.description = 'Running'
            status.button_style = 'info'            
           
            # define the time [s] relative to initiation of the repeat function
            #np.save('times', np.vstack((t0, np.array(time.time()))))
            t = time.time()-t0
            
            # execute the defined sequence providing t and datafile
            I = sequence(spectrometer)
            #I = lab.OO_dummy['QEPro'].capture()
            # add spectrum as array to database and attach attributes
            entry_name = 't%s' %i
            if zone==None:
                
                db_entry = db.create_array(db.root,entry_name, I['mean_spec'], 'Intensities at time '+str(round(t/3600, 2))+' [h]')
                db_entry.attrs['time_s'] = round(t, 2)
                for attribute in ['Integration time [ms]', 'N']:
                    db_entry.attrs[attribute] = I[attribute]   
            else:
                db_entry = db.create_array(db.root,entry_name, I['mean_spec'], 'Intensities at time '+str(t/3600)+' [h]')
                db_entry.attrs['time_s'] = t
                for attribute in I.keys():
                    db_entry.attrs[attribute] = I[attribute]   
            db.flush()
            i+=1
            # sleep for the specified period of time [min]
            partial = period_minutes*60/100
            for j in range(100):
                time.sleep(partial)
                progress.value = 100-j
            
        elif stop == True:
            # on first pass close datafile access to allow access from other python instances
            db.close()
            
            # adjust status appearance
            status.description = 'Paused'
            status.button_style = 'danger'            
            
           # sleep during a time to avoid unnecessary loop repitions during pause cycles 
            # while providing sufficient reactiveness of the script
            time.sleep(.25)
            
        else:
            # adjust status button appearance
            status.description = 'Finished: Experiment ended by user.'
            status.button_style = '' 
            # Close datafile access and end the loop for good
            db.close()
            break


###======================================================================================

        
def npy2txt(array, filename):
    storeTo='Data/Txt_output/'+str(filename)+'.txt'
    lines=[]
           
    for i in range(len(array)):
        line= ''
        line= line+'\t'+str(array[i])
        line= line+'\n'
        lines.append(line)
               
    with open(str(storeTo), 'w') as fopen:
        for line in lines:
            fopen.write(line)
            
            
def npz2txt(arraylist, filename):
    storeTo='Data/Txt_output/'+str(filename)+'.txt'
    lines=[]
    for i in range(len(arraylist[0])):
        line= ''        
        for j in range(len(arraylist)):
            line= line+'\t'+str(arraylist[j][i])
            line= line+'\n'
            lines.append(line)
            
    with open(str(storeTo), 'w') as fopen:
        for line in lines:
            fopen.write(line)


