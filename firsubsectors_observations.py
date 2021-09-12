# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 16:44:12 2018

@author: TYF

This module defines a class and its methods to consolidate QGIS-processed satellite observations for a month
"""

from collections import OrderedDict
import pandas as pd 
import numpy as np 
import datetime as dt
import calendar
import os
import logging
import csv
import glob

class firsubsectors_observations:    
    def __init__(self, yyyymm, inputpath, outputpath):
        '''
        Initiates an instance that consolidates QGIS-processed satellite observations for a month
        '''
        self.yyyymm = yyyymm
        self.inputpath = inputpath
        self.outputpath = outputpath
        self.observations = OrderedDict()
        self.subsectors = ['SS_1E', 'SS_1W', 'SS_2N', 'SS_2S', 'SS_3', 'SS_4E', 'SS_4W', 'SS_5E', 'SS_5N', 'SS_5S', 'SS_5W', 'SS_6', 'SS_7', 'SS_8E', 'SS_8W']
        
    def consolidate(self):
        '''
        Consolidates satellite observations of a month
        '''
        yyyy, mm = int(str(self.yyyymm)[:4]), int(str(self.yyyymm)[-2:])
        last_day = calendar.monthrange(yyyy, mm)[1]
        date_time = dt.datetime(yyyy, mm, 01, 00, 00) # specify start date_time here 
        end_date_time = dt.datetime(yyyy, mm, last_day, 23, 50) # specify end date_time here
        while date_time <= end_date_time:
            try:
#            filename = '%sH08.H8_ASEAN_1km--L1B.Thunderstorms_FIR.csv' %date_time.strftime('%Y%m%d%H%M')
                filepath = glob.glob(os.path.join(self.inputpath, '*%s*.csv' %date_time.strftime('%Y%m%d%H%M')))[0]
#                filepath = os.path.join(self.inputpath, filename)
                df = pd.read_csv(filepath)
                self.observations[date_time] = OrderedDict()
                for subsector in self.subsectors:
                    ts_percent = df.loc[df['Sector'] == subsector]['TS_Percent'].sum()
                    if ts_percent >= 0.75:
                        self.observations[date_time][subsector] = 3
                    elif ts_percent > 0.5:
                        self.observations[date_time][subsector] = 2
                    elif ts_percent > 0.05:
                        self.observations[date_time][subsector] = 1
                    else:
                        self.observations[date_time][subsector] = 0     
            except Exception, e:
                logging.warning('Observations for %s not read | %s\n' %(date_time, str(e)))
                self.observations[date_time] = OrderedDict()
                ts_percent = -9999
                for subsector in self.subsectors:
                    self.observations[date_time][subsector] = ts_percent
            ### Important ##################################        
            date_time = date_time + dt.timedelta(minutes=10)
            ################################################
            
    def output_observations(self):
        '''
        Outputs the consolidated observations to a CSV file
        '''
        outputfilepath = os.path.join(self.outputpath, 'FIRSubsectors_Observations_%s.csv' %self.yyyymm)
        with open(outputfilepath, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['date_time',] + self.subsectors)
            for date_time in self.observations:
                writer.writerow([date_time.strftime('%Y%m%d %H:%M'),] + [self.observations[date_time][subsector] for subsector in self.subsectors])

    def consolidate_combined(self):
        '''
        Consolidates satellite observations of a month
        '''
        for yyyymm in self.yyyymm:
            yyyy, mm = int(str(yyyymm)[:4]), int(str(yyyymm)[-2:])
            last_day = calendar.monthrange(yyyy, mm)[1]
            date_time = dt.datetime(yyyy, mm, 1, 00, 00) # specify start date_time here
            end_date_time = dt.datetime(yyyy, mm, last_day, 23, 50) # specify end date_time here
            while date_time <= end_date_time:
                try:
#                filename = '%sH08.H8_ASEAN_1km--L1B.Thunderstorms_FIR.csv' %date_time.strftime('%Y%m%d%H%M')
                    filename = glob.glob('*%s*.csv' %date_time.strftime('%Y%m%d%H%M'))[0]
                    filepath = os.path.join(self.inputpath, filename)
                    df = pd.read_csv(filepath)
                    self.observations[date_time] = OrderedDict()
                    for subsector in self.subsectors:
                        ts_percent = df.loc[df['Sector'] == subsector]['TS_Percent'].sum()
                        if ts_percent >= 0.75:
                            self.observations[date_time][subsector] = 3
                        elif ts_percent > 0.5:
                            self.observations[date_time][subsector] = 2
                        elif ts_percent > 0.05:
                            self.observations[date_time][subsector] = 1
                        else:
                            self.observations[date_time][subsector] = 0     
                except Exception, e:
                    logging.warning('Observations for %s not read | %s\n' %(date_time, str(e)))
                    self.observations[date_time] = OrderedDict()
                    ts_percent = -9999
                    for subsector in self.subsectors:
                        self.observations[date_time][subsector] = ts_percent
                ### Important ##################################        
                date_time = date_time + dt.timedelta(minutes=10)
                ################################################
            
    def output_observations_combined(self):
        '''
        Outputs the consolidated observations to a CSV file
        '''
        outputfilepath = os.path.join(self.outputpath, 'FIRSubsectors_Observations_Combined.csv')
        with open(outputfilepath, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['date_time',] + self.subsectors)
            for date_time in self.observations:
                writer.writerow([date_time.strftime('%Y%m%d %H:%M'),] + [self.observations[date_time][subsector] for subsector in self.subsectors])


#yyyymm = 201807
#inputpath = r'D:\SatTS\FIRSubsectors_Evaluation\Observations'
#outputpath = r'D:\SatTS\FIRSubsectors_Evaluation'
#
#a = firsubsectors_observations(yyyymm, inputpath, outputpath)
#a.consolidate()
#a.output_observations()