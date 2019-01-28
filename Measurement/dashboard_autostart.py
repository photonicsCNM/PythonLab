#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: tobiasnils
"""
# =============================================================================
# Dependencies
# =============================================================================

import os as os
import getpass

import numpy as np
import pandas as pd
import json
from datetime import datetime

from modules.MyDB import MyDB

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import row, column , widgetbox
from bokeh.models import ColumnDataSource, Legend, LegendItem, DatetimeTickFormatter
import bokeh.models.tools as tools
from bokeh.models.glyphs import Line, Quad
from bokeh.models.widgets import Select, Slider, RangeSlider, Paragraph, Panel, Tabs, MultiSelect
from bokeh.palettes import Blues4, Greens, Blues
from bokeh.plotting import output_file, show
from tornado import gen
import threading
import time as time
import matplotlib.cm as cm

# =============================================================================
# Define Helper Functions
# =============================================================================
class DashBoard():

    def __init__(self, log_dir='.', roll_over=100):
        self.roll_over = roll_over
        self.get_experiment(log_dir)
        self.get_data()
        self.update_timeseries()
        LogPanel = self.get_log(log_dir)
        # ============= feed data to bokeh =====================
        self.timeseries_sources ={sensor:ColumnDataSource() for sensor in self.sensors}
        self.wl_slider = Slider(title="Represented Wavelength [nm]",
                                value=600, start=450, end=725, step=1)
        self.update_sources_for_timeseries('value', 600, 600)
        self.wl_slider.on_change('value', self.update_sources_for_timeseries)
        TimeGraph = self.create_time_plot()
        TimeTabs = Tabs(tabs=[TimeGraph, LogPanel])
        self.TimePanel = Panel(child=TimeTabs, title='Signal over time')

        self.spectral_sources ={sensor:ColumnDataSource() for sensor in self.sensors}
        self.date_selection = Select(title='Pick a date',
                                        options=self.dates,
                                        value=self.dates[-1],
                                        )
        self.SpectralPanel = self.create_spectral_plot()
        self.update_sources_for_spectral_plot('value', [self.dates[-1]],
        [self.dates[-1]])
        self.date_selection.on_change('value', self.update_sources_for_spectral_plot)


    @gen.coroutine
    def update_panels(self):
        new_files = self.db.new_files
        if new_files:
            self.update_timeseries()
            self.update_sources_for_timeseries('value', 600, 600)
            self.date_selection.options = self.dates
            self.update_sources_for_spectral_plot('value', [self.dates[-1]],
            [self.dates[-1]])

        else:
            pass
        # time.sleep(1)

    def Loss(self, intensity_readout, initial_intensity):
        """returns optical power loss in dB"""
        return 10*np.log10(initial_intensity/intensity_readout)
    def stats(self, list):
        N = len(list)
        return np.nanmean(list, axis=0), np.nanstd(list, axis=0), N
    def find_closest(self, A, target):
        #A must be sorted
        idx = A.searchsorted(target)
        idx = np.clip(idx, 1, len(A)-1)
        left = A[idx-1]
        right = A[idx]
        idx -= target - left < right - target
        return idx

    def create_time_data(self, mode='auto-reference'):
        """
        variables = ['time [s]', 'temperature [dgC]']
        observations = ['Loss (λ)']
        constants = ['wavelengths [λ]'], used as indeces
        """
        dataset = self.create_dataset()
        spectra = {key:[] for key in dataset}
        spectra_min = {key:[] for key in dataset}
        spectra_max = {key:[] for key in dataset}
        dataframes = {}
        # stats(some_measurement.get_data())
        for key in dataset:
            initial_intensity = np.nanmean(dataset[key][0].get_data(),
            axis=0)[self.wl1:self.wl2]
            time = []
            for Measurement in dataset[key][1:]:

                time_stamp = Measurement.metadata['timestamp']
                time.append(pd.to_datetime(time_stamp, format='%Y_%m_%d-%Hh%M'))
                if mode=='auto-reference':
                    #offset = np.mean(100-(reference['intensities']/reference_t0['intensities']*100), axis=0)
                    Sn_t = self.Loss([i[self.wl1:self.wl2] for i in Measurement.get_data()],
                    initial_intensity)
                    S_mean, S_std, N = self.stats(Sn_t)
                    S_min = S_mean - S_std
                    S_max = S_mean + S_std
                    #spectra.append([pd.Series(S_i, index=np.round(wavelengths, 2)) for S_i in S_n_t])
                    spectra[key].append(pd.Series(S_mean, index=np.round(self.wavelengths, 2)))
                    spectra_min[key].append(pd.Series(S_min, index=np.round(self.wavelengths, 2)))
                    spectra_max[key].append(pd.Series(S_max, index=np.round(self.wavelengths, 2)))

                else:
                    raise AttributeError('mode not defined.')

            df = pd.DataFrame()
            df['time'] = time
            # timedelta here instead of pd.DateOffset to avoid pandas bug < 0.18 (Pandas issue #11925)
            df['left'] = [time[0]-abs(time[1]-time[0])/2]+[t-abs(t-time[i-1])/2 for i,
            t in enumerate(time)][1:]
            df['right'] = [time[0]+abs(time[1]-time[0])/2]+[t+abs(t-time[i-1])/2 for i,
            t in enumerate(time)][1:]
            df = df.set_index(['time'])
            df.sort_index(inplace=True)
            df['average'] = spectra[key]
            df['minimum'] = spectra_min[key]
            df['maximum'] = spectra_max[key]
            dataframes[key] = df

        return dataframes, [str(t) for t in time]
# =============================================================================
# Set directories and file names for logging
# =============================================================================
    def get_experiment(self, log_dir):
        # set directories and file names for logging
        user = getpass.getuser()
        # log_dir = '/home/%s/notebooks/MyOpticsLab/Measurement'%(user)
        # log_dir='.'
        log_file = 'log.txt'

        saving_to = []
        with open(os.path.join(log_dir,log_file), 'r') as log:
            for line in log.readlines():
                if 'Saving data to: ' in line:
                    saving_to.append(line.split(': ')[-1].split('\n')[0])
        saving_to = saving_to[-1]
        saving_to
        # for testing on ideaPad:
        saving_to = saving_to.split('/')
        saving_to=saving_to[-2]
        os.path.join(saving_to ,'acquisition.settings')
        # load settings from file
        with open(os.path.join(saving_to ,'acquisition.settings'), 'r') as settings_bak:
            settings = json.load(settings_bak)

        self.experiment = settings['experiment']
        self.sensors = {'Sensor %i'%(i+1):sensor for i, sensor in enumerate(settings['sensors'])}
# =============================================================================
# Load data and information
# =============================================================================
    def get_data(self):
        self.db=MyDB()
        self.dataset = self.create_dataset()
        measurement = [Measurement for Measurement in self.dataset.values()][0][0]
        # print(measurement.path)
        wavelengths = self.db.spectrometers[measurement.metadata['detector']]
        self.wl1 = self.find_closest(wavelengths, 400)
        self.wl2 = self.find_closest(wavelengths, 750)
        self.wavelengths = wavelengths[self.wl1:self.wl2]
    def create_dataset(self):
        if len(self.db.data) <= self.roll_over:
            return {sensor:self.db.sort(self.db.query(self.experiment,
                                    self.sensors[sensor]),
                                    'timestamp') for sensor in self.sensors}
        else:
            query = {sensor:self.db.sort(self.db.query(self.experiment,
                                    self.sensors[sensor]),
                                    'timestamp') for sensor in self.sensors}
            return {sensor:query[sensor][0:1]+query[sensor][-self.roll_over:] for sensor in self.sensors}
    def update_timeseries(self):
        self.TimeData, self.dates = self.create_time_data()
    def get_log(self, log_dir):
        log_text = []
        with open(os.path.join(log_dir,'log.txt')) as log:
            for line in log.readlines():
                log_text.append(Paragraph(text=line))
                log_header = Paragraph(text='Incidents-Log:')
                view_log = column(log_header)
                for line in log_text:
                    view_log.children.append(line)
        return Panel(child=view_log, title='Incidents')
    def update_sources_for_timeseries(self, attr, old, new):
        val = self.wl_slider.value
        idx = self.find_closest(self.wavelengths, val)
        idx = round(self.wavelengths[idx], 2)
        for key in self.dataset:
            df = self.TimeData[key]
            df_updated = pd.DataFrame()
            df_updated['time'] = df.index
            df_updated = df_updated.set_index(['time'])
            df_updated.sort_index(inplace=True)
            df_updated['left'] = df['left']
            df_updated['right'] = df['right']
            df_updated['average'] = pd.Series([S[idx] for S in df.average], index=df.index)
            df_updated['minimum'] = pd.Series([S[idx] for S in df.minimum], index=df.index)
            df_updated['maximum'] = pd.Series([S[idx] for S in df.maximum], index=df.index)
            self.timeseries_sources[key].data = ColumnDataSource.from_df(df_updated)
    def create_time_plot(self):
        timeline = figure(x_axis_type="datetime", plot_width=800, #tools="",
                        toolbar_location='right',  toolbar_sticky=False)
        timeline.title.text = 'Response over time'
        timeline.yaxis.axis_label = 'Optical Power Variation [dB]'
        timeline.xaxis.axis_label = 'Time'
        timeline.xaxis.formatter = DatetimeTickFormatter(hours=["%H:%M"],
                                                        days=['%d/%m/%Y'],
                                                        months=['%m/%Y'])
        timeline.xaxis.major_label_orientation = np.pi/4
        palettes = [Blues4, Greens[4]]
        for i, key in enumerate(self.timeseries_sources):
            source = self.timeseries_sources[key]
            timeline.line(source=source, x="time", y="average", line_color=palettes[i][0],
            line_width=2,
            line_alpha=0.9,
            legend = key)
            timeline.quad(source=source, top='maximum', bottom='minimum',
                        left='left',
                        right='right',
                        fill_color=palettes[i][1],
                        fill_alpha=0.4,
                        line_color=palettes[i][1],
                        line_alpha=0.6,
                        legend = key+' | Standard deviation')
        timeline.legend.location = "top_left"
        timeline.legend.click_policy="hide"
        return Panel(child=column(timeline, self.wl_slider), title='Signal')
    def convert_timestamp(self, date_time):
        time_stamp = str(date_time).split()
        date, time = time_stamp[0],  time_stamp[1]
        date = date.replace('-', '_')
        time = time[:-3].replace(':', 'h')
        time_stamp = date+'-'+time
        return time_stamp
    def compile_spectral_response(self, sensor, time_stamp, mode='auto-reference'):
        if mode=='auto-reference':
            # print(self.experiment)
            initial_intensity = np.nanmean(self.dataset[sensor][0].get_data(),
                                    axis=0)[self.wl1:self.wl2]
            #offset = np.mean(100-(reference['intensities']/reference_t0['intensities']*100), axis=0)
            Sn_t = self.Loss([i[self.wl1:self.wl2] for i in self.db.query(
                                    self.experiment,self.sensors[sensor],
                                        time_stamp).get_data()],
                                                initial_intensity)
            S_mean, S_std, N = self.stats(Sn_t)
            return S_mean
        else:
            raise AttributeError('mode not defined.')
    def create_spectral_plot(self):
        self.spectral_plot = {}
        self.displayed_spectra = []
        colors = [Blues, Greens]
        for palette, sensor in enumerate(self.sensors):
            p = figure(x_range=(450,720), y_range = (-5,5),
                            # plot_width=600, #tools="",
                            toolbar_location='right',  toolbar_sticky=False)
            p.title.text = 'Spectral Response | %s'%sensor
            p.xaxis.axis_label='Wavelength [nm]'
            p.yaxis.axis_label='Optical Power Variation [dB]'
            self.spectral_plot[sensor] = p
        self.spectral_plot['counter'] = 0
        self.spectral_plot['Sensor 2'].x_range = self.spectral_plot[
                                                'Sensor 1'].x_range
        self.spectral_plot['Sensor 2'].y_range = self.spectral_plot[
                                                'Sensor 1'].y_range
        spectral_view = row(self.date_selection,
                            self.spectral_plot['Sensor 1'],
                            self.spectral_plot['Sensor 2'])
        return Panel(child=spectral_view, title='Spectral Response')
    def update_sources_for_spectral_plot(self, attrname, old, new):
        date_time = self.date_selection.value
        i = self.spectral_plot['counter']
        colors = [Blues, Greens]
        for palette, sensor in enumerate(self.sensors):
            source = {'wl':self.wavelengths}
            time_stamp = self.convert_timestamp(date_time)
            data = self.compile_spectral_response(sensor, time_stamp)
            # spectra.append(data)
            source[date_time] = data
            self.spectral_sources[sensor].data=source
            self.spectral_plot[sensor].line(x='wl', y = date_time,
                                source=self.spectral_sources[sensor],
                                 color=colors[palette][9][i],line_width=2,
                                 legend=time_stamp, name=time_stamp)
            # self.spectral_plot[sensor].title.text = 'Spectral Response | %s'%sensor
            self.spectral_plot[sensor].legend.location = "top_left"
            self.spectral_plot[sensor].legend.click_policy="hide"
        if self.spectral_plot['counter'] < 9:
            self.spectral_plot['counter']+=1
        else:
            self.spectral_plot['counter'] = 0
# if __name__=='__main__':
dashboard = DashBoard(roll_over=500)
# dashboard.experiment
# dashboard.db.list_experiments()


doc = curdoc()
doc.title = dashboard.experiment
doc.add_periodic_callback(dashboard.update_panels, 1000)
doc.add_root(Tabs(tabs=[dashboard.TimePanel, dashboard.SpectralPanel]))
import bokeh
