#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  3 16:40:15 2018

@author: nils
"""
# Dependencies:
# 3rd party; shipped with conda
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime
import os
import getpass
import traceback
import json

# Own stuff
from modules import GPIO

# Suppress Warnings
import warnings
warnings.filterwarnings("ignore")


class Measurement():
    
    def __init__(self, OO, **settings):
        
        # set directories and file names for logging
        user = getpass.getuser()
        self.log_dir = '/home/%s/notebooks/MyOpticsLab/Measurement/'%(user)

        try: 
            self.name = settings['experiment']

            self.spectrometer = OO[settings['detector']]
            self.sensors = settings['sensors']
            for sensor in self.sensors.keys():
                self.sensors[sensor]['switch'] = GPIO.Switch(
                                                    self.sensors[sensor]['GPIO-pin'])
            self.directory = settings['dir']
            if not os.path.exists(self.directory):
                os.mkdir(self.directory)

            if not 't0' in settings.keys():
                self.t0 = time.time()     
                settings['t0'] = self.t0
            else:
                self.t0 = settings['t0']
            
            def jdefault(o):
                return o.__dict__

            with open(self.directory+'acquisition.settings', 'w') as settings_bak:
                json.dump(settings, settings_bak, indent=4, default=jdefault)
            
        except Exception:
                f = open(self.log_dir +'log.txt', 'a+')
                traceback.print_exc(file=f)
                f.close()
                
                
    def log(self, incidence):
        """
        add message-lines to log.txt
        """
        with open(self.log_dir +'/log.txt', 'a+') as log:
            incidence = str(datetime.now()) + '\t' + incidence +'\n'
            log.write(incidence)
                
    def acquisition_sequence(self, detector, IT, N, gpio_switch):        
        """
        base function to be used in more complex routines
        """
        detector.set_IT(IT)
        Idark_n, I_n= [],[]
        
        for i in range(N):
            
            gpio_switch.low()
            Idark_n.append(detector.multiple_spectra(1))
            time.sleep(.5)
            gpio_switch.high()
            I_n.append(detector.multiple_spectra(1))
            time.sleep(.5)
        gpio_switch.low()
        
        for i in range(N):
            I_n[i]['intensities'] = I_n[i]['intensities'] - Idark_n[i]['intensities']
            
        I = {'intensities':[I_n[i]['intensities'] for i in range(N)], 'IT':detector.IT, 'N':N, 'detector':detector.name}
        return I
    
    def arrays2txt(self, arraylist, filename):
        """
        save multiple columns of array data to a single (tab separated) text file
        """
        storeTo=str(filename)+'.txt'
        lines=[]
        
        for i in range(len(arraylist[0])):
            line= ''        
            for j in range(len(arraylist)):
                line= line+'\t'+str(arraylist[j][i])
                
            line= line+'\n'
            lines.append(line)
                
        with open(str(storeTo), 'a+') as fopen:
            for line in lines:
                fopen.write(line)
    
    def save_intensities(self, label, N, as_txt = False, confirm = False):
        timestamp = datetime.now().strftime('%Y_%m_%d-%Hh%M')
        for i,key in enumerate(self.sensors.keys()):
            I = self.acquisition_sequence(self.spectrometer, self.sensors[key]['IT'], N, self.sensors[key]['switch'])
            fig = plt.figure()
            fig.suptitle(key)
            axis = fig.add_subplot(111)
            for dataset in I['intensities']:
                axis.plot(self.spectrometer.WL, dataset, label=label)           
            
            tags = [self.name, 
                    key, 
                    timestamp,
                    label]
            details = {'tags': tags}
            
            # store data to file
            storeTo = self.directory+'/'+timestamp+'_'+key
            
            if as_txt:
                # create Header
                with open(str(storeTo)+'.txt', 'a+') as fopen:
                    for tag in tags:
                        fopen.write(tag)
                    for key in ['N', 'IT', 'detector']:
                        fopen.write(key+': '+str(I[key]))
                    fopen.write('#==========================================#')                        
                columns = [self.spectrometer.WL]+I['intensities']
                self.arrays2txt(columns, str(storeTo)+'.txt')
            else:
                np.savez_compressed(storeTo, **{ **details, **I})
            
            if confirm:
                input('Press ENTER to proceed.')
            fig.show()
    
    def test_intensities(self, N, confirm=False):
        for i,key in enumerate(self.sensors.keys()):
            I = self.acquisition_sequence(self.spectrometer, self.sensors[key]['IT'], N, self.sensors[key]['switch'])
            fig = plt.figure()
            fig.suptitle(key)
            axis = fig.add_subplot(111)
            for dataset in I['intensities']:
                axis.plot(self.spectrometer.WL, dataset, label=key)
            fig.show()
            if confirm:
                input('Press ENTER to proceed.')
                    
            
    def start_repetition(self):
        
        incidence = 'Starting data acquisition: '
        self.log(incidence)
        path  = 'Saving data to: ' + self.directory
        self.log(path)
        indicator = GPIO.Switch(25)
        try:
            while True:
                try:
                    with open(self.directory+'acquisition.params', 'r') as params_bak:

                        params = json.load(params_bak)

                        stop = params['stop']
                        period_minutes = params['period [min]']
                        N = params['N']

                    if stop:
                        indicator.low()
                        self.log('Acquisition cycle stopped by user.')
                        break

                    elif not stop:               

                        #start to assess total duration of measurement
                        acquisition_init = time.time()

                        timestamp = datetime.now().strftime('%Y_%m_%d-%Hh%M')
                        for key in self.sensors.keys():
                            tags = [self.name, 
                                    key, 
                                    timestamp]
                            details = {'tags': tags, 
                                       'period [min]':period_minutes, 
                                       'time':[self.t0, acquisition_init-self.t0]}
                            I = self.acquisition_sequence(self.spectrometer, 
                                                          self.sensors[key]['IT'], 
                                                          N, 
                                                          self.sensors[key]['switch'])
                            np.savez_compressed(self.directory+'/'+timestamp+'_'+key, 
                                                **{ **details, **I})
                            del I

                        # end assessment of duration of measurement
                        acquisition_duration = time.time() - acquisition_init

                        idle_time = period_minutes*60 - acquisition_duration
                        idle_init = time.time()
                        while True:
                            with open(self.directory+'acquisition.params', 'r') as params_bak:

                                params = json.load(params_bak)

                                stop = params['stop']
                                period_minutes = params['period [min]']
                                N = params['N']
                            if stop:
                                break
                            else:
                                seconds_passed = time.time() - idle_init
                            #    print(seconds_passed, 'seconds passed')
                                if seconds_passed >= (idle_time):
                            #        print('defined idle time was',idle_time )
                                    indicator.high()
                                    break
                                else:
                                    indicator.high()
                                    time.sleep(.2)
                                    indicator.low()
                                    time.sleep(1.5)
                    else:
                        time.sleep(.25)

                except Exception:
                    indicator.low()
                    with open(self.log_dir +'log.txt', 'a+') as f:
                        traceback.print_exc(file=f)
        except KeyboardInterrupt:
            indicator.low()
            message ='Acquisition cycle stopped by user.'
            print(message)
            self.log(message)
