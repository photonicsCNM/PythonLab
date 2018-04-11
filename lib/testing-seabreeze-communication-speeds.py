# -*- coding: utf-8 -*-
"""
Testing communication speed of Ocean Optics QE65000 series and TTL shutter

Created on Fri Jan 20 16:30:14 2017

@author: nils
"""
import time
sleeping_time =0

# Vary sleeping times in ms after turning on the light 
#(shutter logic is inverse)
n=4

sleeping_time =0

for i in range(7):
    sleeping_time+=.01

    start= time.time()
    b=[]
    MyLab.light_switch.access.lamp_set_enable(False)
    time.sleep(sleeping_time)
    for i in range(n):
        a = sp1.get_signal()
        b.append(a)
        print(time.time()-start)
    MyLab.light_switch.access.lamp_set_enable(True)
    plt.figure()
    for i in range(n):
        plt.plot(wl,b[i], label='spectra['+str(i)+'] with 70ms pause', alpha=.5)
    plt.legend(fontsize=9)
    print('done')
    
# Do the same using continuous strobe function
    
sleeping_time =0

for i in range(7):
    sleeping_time+=.01

    start= time.time()
    b=[]
    MyLab.light_switch.access.continuous_strobe_set_enable(False)
    time.sleep(sleeping_time)
    for i in range(n):
        a = sp1.get_signal()
        b.append(a)
        print(time.time()-start)
    MyLab.light_switch.access.continuous_strobe_set_enable(True)
    plt.figure()
    for i in range(n):
        plt.plot(wl,b[i], label='spectra['+str(i)+'] with 70ms pause', alpha=.5)
    plt.legend(fontsize=9)
    print('done')

#Look at average of last three sleeping times in ms after 
    
sleeping_time =0

for i in range(7):
    sleeping_time+=.01
    
    plt.figure()
    start= time.time()
    b=[]
    MyLab.light_switch.access.continuous_strobe_set_enable(False)
    time.sleep(sleeping_time)
    for i in range(n):
        a = sp1.get_signal()
        b.append(a)
        print(time.time()-start)
    MyLab.light_switch.access.continuous_strobe_set_enable(True)
    
    plt.plot(wl,np.average(b[1:], axis=0), label='avg[1:]_n='+str(n)+'_'+str(sleeping_time*1000)+'ms-pause', alpha=.5)
    plt.legend(fontsize=9)
    print('done')