#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper function for repeating a function with a period and storing data in hdf5 format.

Created on Fri Apr 13 2018

@author: tobiasnils

"""

def repeat(sequence, spectrometer, period_minutes = .05, write_to = 'database', experiment_name=None):
       
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
    if experiment_name==None:
        pass
    else:
        db_group = db.create_group(db.root, experiment_name, 'Measurements at '+experiment_name)    
    
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
            if experiment_name==None:                
                db_entry = db.create_array(db.root,entry_name, I['mean_spec'], 'Intensities at time '+str(round(t/3600, 2))+' [h]')
                db_entry.attrs['time_s'] = round(t, 2)
                for attribute in ['IT', 'N']:
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
