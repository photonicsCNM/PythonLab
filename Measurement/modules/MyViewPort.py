def find_closest(A, target):
    #A must be sorted
    idx = A.searchsorted(target)
    idx = np.clip(idx, 1, len(A)-1)
    left = A[idx-1]
    right = A[idx]
    idx -= target - left < right - target
    return idx

class ViewPort():

    widgets = __import__('ipywidgets')
    pd = __import__('pandas')
    mpl = __import__('matplotlib')
    plt = mpl.pyplot
    
    def __init__(self, df):
        
        self.df = df
        
        if type(df)==dict:            
            
            self.attrs = {'ylabel': 'Intensity [a. u.]',
                          'legend': 'Intensity over time',
                         }
            
            self.key = self.widgets.RadioButtons(options=df.keys(),
                                                        value = 'biofilm',
                                                        disabled=False)    
            
            self.interactive_df = self.df[self.key.value]
            self.time = self.df[self.key.value].index
            def action(key):
                self.interactive_df = self.df[key]
            self.select_key = self.widgets.interactive(action, key=self.key)
            
            
        else:
            self.time = df.index
            self.attrs = {'ylabel': 'Transmission/%',
                          'legend': 'Transmission over time',
                         }
            self.interactive_df = self.df  
            
        self.selected_time = self.interactive_df.index[-1]
        self.wavelength_range = (self.interactive_df[self.selected_time][0].index[400],self.interactive_df[self.selected_time][0].index[-400])
        
        self.wl_range_selector = self.widgets.SelectionRangeSlider(
                                                        options=self.interactive_df[self.selected_time][0].index,
                                                        #value = (405.02,745.76),
                                                        description=' ',
#                                                         layout=Layout(width='200%', height='50px'),
                                                        continuous_update =False,
                                                        disabled=False
                                                        )
        
        self.wl_index = self.widgets.Dropdown(options = self.interactive_df[self.selected_time][0].index,
                                         #value=540.9,
                                        disabled=False)
        self.time_units = self.widgets.RadioButtons(options=['min', 'h', 'days', 'weeks'],
                                               value = 'h',
                                              disabled=False)
        
        self.wl_range = self.widgets.HBox([self.widgets.Label('define wavelength range [nm]'), self.wl_range_selector])
        self.Figure = self.widgets.interactive(self.interact_Figure, unit = self.time_units, wl_index=self.wl_index)
#         display(HBox([Label('define wavelength range [nm]'), self.wl_range_selector]), 
#                 Figure)
        
    def interact_Figure(self, unit, wl_index):
        self.fig = self.plt.figure(num='Interactive Data Display', figsize=(10, 10), dpi=80)
        self.timeline = self.fig.add_subplot(212)
#         self.timeline.set_title('click on points')
        self.timeline.set_xlabel('time [h]')
        self.timeline.set_ylabel(self.attrs['ylabel'])
        
        self.spectral_plot = self.fig.add_subplot(211)
#         self.Abs_plot.set_title('Absorbance [A.U.] spectrum at time $t_0$')
        self.spectral_plot.set_xlabel('Wavelength [nm]')
        self.spectral_plot.set_ylabel(self.attrs['ylabel'])
#         self.Abs_plot.autoscale(enable=True, axis='y', tight=False)
        
        self.N = len(self.interactive_df[self.interactive_df.index[1]])            
        
        if unit=='min':
            self.timeline.clear()
            self.timeline.set_xlabel('time [min]')
            self.timeline.set_ylabel(self.attrs['ylabel'])
            self.interactive_df = self.pd.Series(self.interactive_df.values, index = self.time/60)
        if unit=='h':
            self.timeline.clear()            
            self.timeline.set_xlabel('time [h]')
            self.timeline.set_ylabel(self.attrs['ylabel'])
            self.interactive_df = self.pd.Series(self.interactive_df.values, index = self.time/60/60)
        if unit=='days':
            self.timeline.clear()
            self.timeline.set_xlabel('time [days]')
            self.timeline.set_ylabel(self.attrs['ylabel'])
            self.interactive_df = self.pd.Series(self.interactive_df.values, index = self.time/60/60/24)  
        if unit=='weeks':
            self.timeline.clear()
            self.timeline.set_xlabel('time [weeks]')
            self.timeline.set_ylabel(self.attrs['ylabel'])
            self.interactive_df = self.pd.Series(self.interactive_df.values, index = self.time/60/60/24/7)          
                
        times=self.interactive_df.index[1:]
        self.selected_time = times[-1]
        
        for n in range(self.N-1):            
            self.timeline.plot(times, [self.interactive_df[time][n][wl_index] for time in times], 
                            'o',markersize=3,
                            c='k', picker=5)
        self.timeline.plot(times, [self.interactive_df[time][self.N-1][wl_index] for time in times], 
                                'o',markersize=3,
                                c='k', picker=5,
                               label = '%s, $N=%i$'%(self.attrs['legend'],self.N))
#         self.timeline.set_xdata([time/60 for time in times])
        self.ylims = self.timeline.get_ylim()
        self.timeline.plot((times[0],times[0]), self.ylims,'-.', c='0.5')
        self.timeline.legend()
        
        self.fig.canvas.mpl_connect('pick_event', self.onpick)
        self.show_Spectra()
        self.fig.show()
        self.plt.tight_layout()
        

    def onpick(self, event):  

        thisline = event.artist
        self.line = thisline
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()
        ind = event.ind
        points = tuple(zip(xdata[ind], ydata[ind]))
        self.timeline.lines[-1].remove()
        self.selected_time = points[0][0]
        self.cursor, = self.timeline.plot((points[0][0],points[0][0]), self.ylims, '-.', c='0.5')
        self.timeline.set_ylim(self.timeline.get_ylim())
        self.show_Spectra()
        
        self.plt.tight_layout()
        
    def set_wavelength_range(self, wavelength_range):
        self.wavelength_range = wavelength_range
        
    def show_Spectra(self):        
        wl1=self.wl_range_selector.value[0]
        wl2=self.wl_range_selector.value[1]
        try:
            for n in range(len(self.interactive_df[self.selected_time])):
                self.spectral_plot.lines[-1].remove()
        except IndexError:
            pass
        
#         self.Abs_plot.set_title('Absorbance [A.U.] spectrum at $t=%f$ %s' %(self.selected_time,self.time_units.value))        
        for n in range(len(self.interactive_df[self.selected_time])):
            if n==0:
                self.spectral_plot.plot(self.interactive_df[self.selected_time][n][wl1:wl2],'o', c='0.5',markersize=1.5, 
                                   label= '$t=%f$ %s' %(self.selected_time,self.time_units.value))
            else:
                self.spectral_plot.plot(self.interactive_df[self.selected_time][n][wl1:wl2], 'o',c='0.5',markersize=1.5)
                
#         self.Abs_plot.set_xlim((wl1,wl2))
#         self.Abs_plot.set_ylim((0.02,.8))
        self.spectral_plot.legend()
        #self.spectral_plot.relim(visible_only=True)     
        #self.spectral_plot.set_ylim((0, 150))

