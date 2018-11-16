#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 18:15:53 2018

@author: nils
"""
# =============================================================================
# Dependencies
# =============================================================================

import os as os
import getpass

import numpy as np
import json
from datetime import datetime

#import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation 
#import ipywidgets as widgets
#from ipywidgets import interact
#from IPython.display import display

import seabreeze as sb
sb.use('cseabreeze')
import seabreeze.spectrometers as sbs

# Own stuff
import modules
from modules import GPIO
from modules.MyOpticsLab import MyOpticsLab
from modules.MyMeasurement import Measurement


# =============================================================================
# Set directories and file names for logging
# =============================================================================

# set directories and file names for logging
user = getpass.getuser()
log_dir = '/home/%s/notebooks/MyOpticsLab/Measurement/'%(user)
log_file = 'log.txt'

def print_log(text):
    with open(log_dir+log_file, 'a+') as log:
        incidence = text + '\n'
        log.write(incidence)

print_log('Re-initialising data acquisition after reboot.')

saving_to = []
with open(log_dir+log_file, 'r') as log:
    for line in log.readlines():
        if 'Saving data to: ' in line: 
            saving_to.append(line.split(': ')[-1].split('\n')[0])
saving_to = saving_to[-1]

# =============================================================================
# Get MyLab up and running
# =============================================================================
# invoke and initialize MyLabOptica instance

MyLab = MyOpticsLab(os, sl=None, sbs=sbs)

#import matplotlib.animation as animation

if len(MyLab.devices) > 0:
    # Setup Spectrometers
    from modules.MySpectrometer import MySpectrometer   
    MyLab.NonlinCorrect = False
    MyLab.DarkCurrentCorrect = False
    OO = {}
    
    # Create ViewPort for live plot of intensities
#    ViewPort = plt.figure('Live Data Feed', figsize=(8,6))
    
#    spec_count = len(MyLab.devices)
#    if spec_count == 1:
#        slots = [ViewPort.subplots(spec_count, sharex=True, sharey=True)]
#    else:
#        slots = ViewPort.subplots(spec_count, sharex=True, sharey=True)

    for i,device in enumerate(MyLab.devices):
        # Create a Seabreeze instance
        OO[MyLab.SeaBreeze_dict[str(device)]] = MySpectrometer(sb, sbs, MyLab, device)
        OO[MyLab.SeaBreeze_dict[str(device)]].name = MyLab.SeaBreeze_dict[str(device)]
        OO[MyLab.SeaBreeze_dict[str(device)]].set_IT(MyLab.IT)
        print('\n Connected to',MyLab.SeaBreeze_dict[str(device)])
        # Start corresponding data Live Feed
#        OO[MyLab.SeaBreeze_dict[str(device)]].start_stream(ViewPort, slots[i])
#    MyLab.LabControls_show()

else:
    print('\n No Ocean Optics devices connected.')
    

# =============================================================================
# Initiate Measurement 
# =============================================================================

# load settings from file
with open(saving_to +'acquisition.settings', 'r') as settings_bak:
    settings = json.load(settings_bak)

M = Measurement(OO, **settings)
M.start_repetition()








