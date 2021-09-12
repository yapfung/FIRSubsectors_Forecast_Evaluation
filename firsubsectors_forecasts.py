# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 11:56:58 2018

@author: TYF

This module defines a class and its methods to extract last ammended FIR subsector forecasts for each forecast period in a month
"""

from collections import OrderedDict
import xml.etree.ElementTree as et
import pandas as pd
import datetime as dt
import os
import logging
import csv

class firsubsectors_forecasts:
    def __init__(self, yyyymm, inputpath, outputpath):
        '''
        Initiates an instance that reads and outputs forecasts
        '''
        self.yyyymm = yyyymm
        self.inputpath = inputpath
        self.outputpath = outputpath
        self.forecasts = []
        self.forecasts_df = None
        
    def time_difference(self, start_time, end_time):
        '''
        Calculates and returns the time difference between two datetime objects in minutes
        '''
        return (start_time - end_time).days*24*60 + (start_time - end_time).seconds/60
        
#    def read_forecasts_xml(self, filepath):
#        '''
#        Reads a forecast xml file and loop through every subsector's forecasts
#        '''
#        tree = et.parse(filepath)
#        root = tree.getroot()
#        issue_date = root[2][1].attrib['date']
#        issue_time = root[2][1].attrib['time'][:-4]
#        validity_start_date = root[2][2].attrib['date']
#        validity_start_time = root[2][2].attrib['time'][:-4]
#        issue_date_time = dt.datetime.strptime(issue_date + issue_time, '%d-%m-%Y%H:%M:%S')
#        validity_start = dt.datetime.strptime(validity_start_date + validity_start_time, '%d-%m-%Y%H:%M')
#        subsectors_xml = root[2][4:]
#        if validity_start not in self.forecasts:
#            self.forecasts[validity_start] = OrderedDict()
#        for subsector_xml in subsectors_xml:
#            self.read_subsector_xml(validity_start, issue_date_time, subsector_xml)
#        
#    def read_subsector_xml(self, validity_start, issue_date_time, subsector_xml):
#        '''
#        Reads the forecasts for a subsector in the forecast xml file and preserve only the last ammended forecasts in attribute self.forecasts
#        The attribute self.forecasts is a nested OrderedDict() that takes the structure of 
#            >> validity_start
#                >> subsector
#                    >> forecast_date_time
#                        >> forecast, category, issue_date_time, lead_time, ammendment, duration
#        '''
#        subsector = subsector_xml.tag
#        if subsector not in self.forecasts[validity_start]:
#            self.forecasts[validity_start][subsector] = OrderedDict()
#        for i, block in enumerate(subsector_xml[0]):
#            date_time = dt.datetime.strptime(str(validity_start.date()) + block.attrib['time'][:5], '%Y-%m-%d%H:%M')
#            if date_time.time() < validity_start.time(): # to add one day for blocks on the next day
#                date_time = date_time + dt.timedelta(days=1)
#            if int(date_time.strftime('%Y%m')) != self.yyyymm: # to exclude data beyond assessment month
#                continue
#            forecast = block.attrib['value']
#            if forecast == 'NilThunderstroms':
#                category = 0
#            elif forecast == 'Isolated':
#                category = 1
#            elif forecast == 'Scattered':
#                category = 2
#            elif forecast == 'Widespread':
#                category = 3
#            lead_time = self.time_difference(date_time, issue_date_time)/60
#            duration = 1
#            if self.time_difference(date_time, validity_start) >= 6*60: # to identify 3-hourly blocks
#                duration = 3
#            if lead_time < 0 or forecast == 'NA': # to omit lapsed blocks 
#                continue
#            if date_time not in self.forecasts[validity_start][subsector]:
#                self.forecasts[validity_start][subsector][date_time] = OrderedDict()
#                self.forecasts[validity_start][subsector][date_time]['forecast'] = forecast
#                self.forecasts[validity_start][subsector][date_time]['category'] = category
#                self.forecasts[validity_start][subsector][date_time]['issue_date_time'] = issue_date_time
#                self.forecasts[validity_start][subsector][date_time]['lead_time'] = lead_time
#                self.forecasts[validity_start][subsector][date_time]['duration'] = duration
#            elif self.forecasts[validity_start][subsector][date_time]['forecast'] == forecast:
#                continue
#            elif self.forecasts[validity_start][subsector][date_time]['issue_date_time'] < issue_date_time:
#                self.forecasts[validity_start][subsector][date_time]['forecast'] = forecast
#                self.forecasts[validity_start][subsector][date_time]['category'] = category
#                self.forecasts[validity_start][subsector][date_time]['issue_date_time'] = issue_date_time
#                self.forecasts[validity_start][subsector][date_time]['lead_time'] = lead_time
#                self.forecasts[validity_start][subsector][date_time]['duration'] = duration
#
#    def output_forecasts(self):
#        '''
#        Read all forecasts xml files and output the forecasts in a CSV file
#        '''
#        for filename in os.listdir(self.inputpath):
#            filepath = os.path.join(self.inputpath, filename)
#            try:
#                self.read_forecasts_xml(filepath)
#            except Exception, e:
#                logging.warning('%s not read | %s' %(filename, str(e)))
#                print '%s not read | %s' %(filename, str(e))
#        outputfilepath = os.path.join(self.outputpath, 'FIRSubsectors_Forecasts_%s.csv' %self.yyyymm)
#        with open(outputfilepath, 'wb') as csvfile:
#            writer = csv.writer(csvfile, delimiter=',')
#            writer.writerow(['validity_start', 'date_time', 'issue_date_time', 'subsector', 'forecast', 'category', 'lead_time', 'duration'])
#            for validity_start in self.forecasts:
#                for subsector in self.forecasts[validity_start]:
#                    for date_time in self.forecasts[validity_start][subsector]:
#                        forecast = self.forecasts[validity_start][subsector][date_time]['forecast']
#                        category = self.forecasts[validity_start][subsector][date_time]['category']
#                        issue_date_time = self.forecasts[validity_start][subsector][date_time]['issue_date_time'].strftime('%Y%m%d %H:%M')
#                        lead_time = self.forecasts[validity_start][subsector][date_time]['lead_time']
#                        duration = self.forecasts[validity_start][subsector][date_time]['duration']
#                        writer.writerow([validity_start, date_time.strftime('%Y%m%d %H:%M'), issue_date_time, subsector, forecast, category, lead_time, duration])
        
    def read_forecasts_xml(self, filepath):
        '''
        Reads a forecast xml file and loop through every subsector's forecasts
        '''
        tree = et.parse(filepath)
        root = tree.getroot()
        issue_date = root[2][1].attrib['date']
        issue_time = root[2][1].attrib['time'][:-4]
        validity_start_date = root[2][2].attrib['date']
        validity_start_time = root[2][2].attrib['time'][:-4]
        issue_date_time = dt.datetime.strptime(issue_date + issue_time, '%d-%m-%Y%H:%M:%S') #changed
        validity_start = dt.datetime.strptime(validity_start_date + validity_start_time, '%d-%m-%Y%H:%M')
        subsectors_xml = root[2][4:]
        for subsector_xml in subsectors_xml:
            self.read_subsector_xml(validity_start, issue_date_time, subsector_xml)
            
    def read_subsector_xml(self, validity_start, issue_date_time, subsector_xml):
        '''
        Reads the forecasts for a subsector in the forecast xml file and store the forecasts in attribute self.forecasts
        '''
        subsector = subsector_xml.tag
        for i, block in enumerate(subsector_xml[0]):
            forecast = block.attrib['value']
            date_time = dt.datetime.strptime(str(validity_start.date()) + block.attrib['time'][:5], '%Y-%m-%d%H:%M')
            if date_time.time() < validity_start.time(): # to add one day for blocks on the next day
                date_time = date_time + dt.timedelta(days=1)
            lead_time = self.time_difference(date_time, issue_date_time)/60
            if self.time_difference(date_time, validity_start) >= 6*60: # to identify 3-hourly blocks
                duration = 3
            else:
                duration = 1
            if int(date_time.strftime('%Y%m')) != self.yyyymm: # to exclude data beyond assessment month
                continue
            if lead_time < 0 or forecast == 'NA': # to omit lapsed blocks 
                continue
            if forecast == 'NilThunderstroms': #changed
                category = 0
            elif forecast == 'Isolated':
                category = 1
            elif forecast == 'Scattered':
                category = 2
            elif forecast == 'Widespread':
                category = 3
            self.forecasts.append([validity_start.strftime('%Y%m%d %H:%M'), date_time.strftime('%Y%m%d %H:%M'), issue_date_time.strftime('%Y%m%d %H:%M'), subsector, forecast, category, lead_time, duration])

    def output_forecasts(self):
        '''
        Read all forecasts xml files and output the forecasts in a CSV file
        '''
        for filename in os.listdir(self.inputpath):
            if str(self.yyyymm) in filename:
                filepath = os.path.join(self.inputpath, filename)
                try:
                    self.read_forecasts_xml(filepath)
                except Exception, e:
                    logging.warning('%s not read | %s\n' %(filename, str(e)))
                    print '%s not read | %s' %(filename, str(e))
        self.forecasts_df = pd.DataFrame(self.forecasts, columns = ['validity_start', 'date_time', 'issue_date_time', 'subsector', 'forecast', 'category', 'lead_time', 'duration'])
        #self.forecasts_df.to_csv(self.outputpath +  '\\test.csv', index = False)
        earliest_issues = self.forecasts_df.groupby(['validity_start', 'date_time', 'subsector', 'forecast']).issue_date_time.transform(min)
        self.forecasts_df = self.forecasts_df.loc[self.forecasts_df.issue_date_time == earliest_issues]
        self.forecasts_df.to_csv(os.path.join(self.outputpath, 'FIRSubsectors_Forecasts_%s.csv' %self.yyyymm))

    def read_forecasts_xml_combined(self, filepath):
        '''
        Reads a forecast xml file and loop through every subsector's forecasts
        '''
        tree = et.parse(filepath)
        root = tree.getroot()
        issue_date = root[2][1].attrib['date']
        issue_time = root[2][1].attrib['time'][:-4]
        validity_start_date = root[2][2].attrib['date']
        validity_start_time = root[2][2].attrib['time'][:-4]
        issue_date_time = dt.datetime.strptime(issue_date + issue_time, '%d-%m-%Y%H:%M:%S')
        validity_start = dt.datetime.strptime(validity_start_date + validity_start_time, '%d-%m-%Y%H:%M')
        subsectors_xml = root[2][4:]
        for subsector_xml in subsectors_xml:
            self.read_subsector_xml_combined(validity_start, issue_date_time, subsector_xml)
            
    def read_subsector_xml_combined(self, validity_start, issue_date_time, subsector_xml):
        '''
        Reads the forecasts for a subsector in the forecast xml file and store the forecasts in attribute self.forecasts
        '''
        subsector = subsector_xml.tag
        for i, block in enumerate(subsector_xml[0]):
            forecast = block.attrib['value']
            date_time = dt.datetime.strptime(str(validity_start.date()) + block.attrib['time'][:5], '%Y-%m-%d%H:%M')
            if date_time.time() < validity_start.time(): # to add one day for blocks on the next day
                date_time = date_time + dt.timedelta(days=1)
            lead_time = self.time_difference(date_time, issue_date_time)/60
            if self.time_difference(date_time, validity_start) >= 6*60: # to identify 3-hourly blocks
                duration = 3
            else:
                duration = 1
            if int(date_time.strftime('%Y%m')) not in self.yyyymm: # to exclude data beyond assessment month
                continue
            if lead_time < 0 or forecast == 'NA': # to omit lapsed blocks 
                continue
            if forecast == 'NilThunderstroms': #changed
                category = 0
            elif forecast == 'Isolated':
                category = 1
            elif forecast == 'Scattered':
                category = 2
            elif forecast == 'Widespread':
                category = 3
            self.forecasts.append([validity_start.strftime('%Y%m%d %H:%M'), date_time.strftime('%Y%m%d %H:%M'), issue_date_time.strftime('%Y%m%d %H:%M'), subsector, forecast, category, lead_time, duration])

    def output_forecasts_combined(self):
        '''
        Read all forecasts xml files and output the forecasts in a CSV file
        '''
        for filename in os.listdir(self.inputpath):
            filepath = os.path.join(self.inputpath, filename)
            try:
                self.read_forecasts_xml_combined(filepath)
            except Exception, e:
                logging.warning('%s not read | %s\n' %(filename, str(e)))
                print '%s not read | %s' %(filename, str(e))
        self.forecasts_df = pd.DataFrame(self.forecasts, columns = ['validity_start', 'date_time', 'issue_date_time', 'subsector', 'forecast', 'category', 'lead_time', 'duration'])
        #self.forecasts_df.to_csv(self.outputpath +  '\\test.csv', index = False)
        earliest_issues = self.forecasts_df.groupby(['validity_start', 'date_time', 'subsector', 'forecast']).issue_date_time.transform(min)
        self.forecasts_df = self.forecasts_df.loc[self.forecasts_df.issue_date_time == earliest_issues]
        self.forecasts_df.to_csv(os.path.join(self.outputpath, 'FIRSubsectors_Forecasts_Combined.csv'))

#inputpath = r'D:\SatTS\FIRSubsectors_Evaluation\Forecasts'     
#outputpath = r'C:\TYF\Satellite_Thunderstorms\Weather Window'       
#a = firsubsectors_forecasts(201807, inputpath, outputpath)
#a.output_forecasts()
