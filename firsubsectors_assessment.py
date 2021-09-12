# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 09:54:12 2018

@author: TYF

This module defines a class that assesses forecasts against observations, calculates scores and outputs the results
"""

import os
import csv
import logging
import datetime as dt
import pandas as pd
from collections import OrderedDict

class firsubsectors_assessment:
    def __init__(self, yyyymm, inputpath, outputpath):
        '''
        Initiates an instance to assess forecasts against observations
        '''
        self.yyyymm = yyyymm
        self.inputpath = inputpath
        self.outputpath = outputpath
        self.assessment = []
        self.assessment_df = None
        
    def assessment_matrix(self, forecasts_category, observations_category):
        '''
        Takes in forecast and observation and returns a tuple of (correct rejections, hit, miss, false alarm)
        '''
        matrix = [[(1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 1, 0), (0, 0, 1, 0)], \
                   [(0, 0, 0, 1), (0, 1, 0, 0), (0, 0.5, 0.5, 0), (0, 0, 1, 0)], \
                   [(0, 0, 0, 1), (0, 0.5, 0, 0.5), (0, 1, 0, 0), (0, 0, 0, 0)],
                   [(0, 0, 0, 1), (0, 0, 0, 1), (0, 0.5, 0, 0.5),(0, 1, 0, 0)]]
        return matrix[int(forecasts_category)][int(observations_category)]
    
    def safe_divide_percentage(self, numerator, denominator):
        '''
        Performs division and return None if undefined
        '''
        if denominator == 0:
            return 'None'
        return numerator/float(denominator)*100
    
    def assess(self):
        '''
        Assesses forecast against all observations within each forecast interval block
        '''
        forecasts_filename = 'FIRSubsectors_Forecasts_%s.csv' %self.yyyymm
        observations_filename = 'FIRSubsectors_Observations_%s.csv' %self.yyyymm
        forecasts_filepath = os.path.join(self.inputpath, forecasts_filename)
        observations_filepath = os.path.join(self.inputpath, observations_filename) 
        try:
            forecasts_df = pd.read_csv(forecasts_filepath)
            observations_df = pd.read_csv(observations_filepath)
        except Exception, e:
            logging.warning(forecasts_filename + ' not assessed | ' + str(e) + '\n')
            print forecasts_filename + ' not assessed | ' + str(e)
        else:
            for row in forecasts_df.iterrows():
                subsector = row[1]['subsector']
                date_time = row[1]['date_time']
                duration = row[1]['duration']
                issue_date_time = row[1]['issue_date_time']
                lead_time = row[1]['lead_time']
                forecasts_category = row[1]['category']
                date_time_end = (dt.datetime.strptime(date_time, '%Y%m%d %H:%M') + dt.timedelta(hours = duration)).strftime('%Y%m%d %H:%M')
                observations_category = observations_df.loc[(observations_df['date_time']>= date_time) & (observations_df['date_time']<= date_time_end)][subsector].max()
                missing_observations = len(observations_df.loc[(observations_df['date_time']>= date_time) & (observations_df['date_time']<= date_time_end) & (observations_df[subsector] == -9999)])
                print date_time
                try:
                    if observations_category < 0:
                        cr, h, m, fa = 0, 0, 0, 0
                    elif missing_observations >= 3 and duration == 1:
                        cr, h, m, fa = 0, 0, 0, 0
                        observations_category = -8888
                    elif missing_observations >= 9 and duration == 3:
                        cr, h, m, fa = 0, 0, 0, 0
                        observations_category = -8888
                    else:
                        cr, h, m, fa = self.assessment_matrix(forecasts_category, observations_category)
                except Exception, e:
                    logging.warning(date_time + ' not assessed | ' + str(e) + '\n')
                    print date_time + ' not assessed | ' + str(e)
                else:
                    self.assessment.append({'date_time': date_time, 'issue_date_time': issue_date_time, 'subsector': subsector, 'lead_time': lead_time, 'forecast_category': forecasts_category, 'observations_category': observations_category, 'cr': cr, 'h': h, 'm': m, 'fa': fa})

    def calculate(self):
        '''
        Calculates scores and outputs the results in a CSV file
        '''
        self.assessment_df = pd.DataFrame(self.assessment,columns = ['date_time', 'issue_date_time', 'subsector', 'lead_time', 'forecast_category', 'observations_category', 'cr', 'h', 'm', 'fa'])
        outputfilename_1 = 'FIRSubsectors_Assessments_%s.csv' %self.yyyymm
        outputfilepath_1 = os.path.join(self.outputpath, outputfilename_1)
        outputfilename_2 = 'FIRSubsectors_Scores_%s.csv' %self.yyyymm
        outputfilepath_2 = os.path.join(self.outputpath, outputfilename_2)
        self.assessment_df.to_csv(outputfilepath_1)
        with open(outputfilepath_2, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([''])
            writer.writerow(['SUMMARY'])
            writer.writerow([''])
            try:
                total_cr = self.assessment_df['cr'].sum()
                total_h = self.assessment_df['h'].sum()
                total_fa = self.assessment_df['fa'].sum()
                total_m = self.assessment_df['m'].sum()
                total_a = self.safe_divide_percentage(total_h + total_cr, total_h + total_cr + total_m + total_fa)
                total_pod = self.safe_divide_percentage(total_h, total_h + total_m)
                total_far = self.safe_divide_percentage(total_fa, total_h + total_fa)
                total_csi = self.safe_divide_percentage(total_h, total_h + total_m + total_fa)               
            except Exception, e:
                logging.warning('Scores unable to be calculated | ' + str(e) + '\n')
                print 'Scores unable to be calculated | ' + str(e)
            else:
                writer.writerow(['total correct rejections', total_cr])
                writer.writerow(['total hits', total_h])
                writer.writerow(['total misses', total_m])
                writer.writerow(['total false alarms', total_fa])
                writer.writerow(['accuracy', total_a])
                writer.writerow(['probablility of detection', total_pod])
                writer.writerow(['false alarm ratio', total_far])
                writer.writerow(['critical success index', total_csi])
                writer.writerow([''])
            writer.writerow(['DETAILS'])
            writer.writerow([''])
            writer.writerow(['subsector', 'cr', 'h', 'm', 'fa', 'a', 'pod', 'far', 'csi']) 
            for subsector in sorted(self.assessment_df['subsector'].unique()):
                try:
                    cr = self.assessment_df[self.assessment_df['subsector'] == subsector]['cr'].sum()
                    h = self.assessment_df[self.assessment_df['subsector'] == subsector]['h'].sum()
                    m = self.assessment_df[self.assessment_df['subsector'] == subsector]['m'].sum()
                    fa = self.assessment_df[self.assessment_df['subsector'] == subsector]['fa'].sum()
                    a = self.safe_divide_percentage(h + cr, h + cr + m + fa)
                    pod = self.safe_divide_percentage(h, h + m)
                    far = self.safe_divide_percentage(fa, h + fa)
                    csi = self.safe_divide_percentage(h, h + m + fa)
                except Exception, e:
                    logging.warning('Scores unable to be calculated for %s | ' %subsector + str(e) + '\n')
                    print 'Scores unable to be calculated for %s | ' %subsector  + str(e)
                else:
                    writer.writerow([subsector, cr, h, m, fa, a, pod, far, csi])
            writer.writerow([''])
            writer.writerow(['lead_time', 'cr', 'h', 'm', 'fa', 'a', 'pod', 'far', 'csi'])    
            for lead_time in sorted(self.assessment_df['lead_time'].unique()):
                try:
                    cr = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['cr'].sum()
                    h = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['h'].sum()
                    m = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['m'].sum()
                    fa = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['fa'].sum()
                    a = self.safe_divide_percentage(h + cr, h + cr + m + fa)
                    pod = self.safe_divide_percentage(h, h + m)
                    far = self.safe_divide_percentage(fa, h + fa)
                    csi = self.safe_divide_percentage(h, h + m + fa)
                except Exception, e:
                    logging.warning('Scores unable to be calculated for %s| ' %lead_time + str(e) + '\n')
                    print 'Scores unable to be calculated for %s | ' %lead_time  + str(e)
                else:
                    writer.writerow([lead_time, cr, h, m, fa, a, pod, far, csi])
            writer.writerow([''])
            writer.writerow(['lead_time', 'subsector', 'cr', 'h', 'm', 'fa', 'a', 'pod', 'far', 'csi'])
            for lead_time in sorted(self.assessment_df['lead_time'].unique()):
                for subsector in sorted(self.assessment_df[self.assessment_df['lead_time'] == lead_time]['subsector'].unique()):
                    try:
                        cr = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['cr'].sum()
                        h = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['h'].sum()
                        m = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['m'].sum()
                        fa = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['fa'].sum()
                        a = self.safe_divide_percentage(h + cr, h + cr + m + fa)
                        pod = self.safe_divide_percentage(h, h + m)
                        far = self.safe_divide_percentage(fa, h + fa)
                        csi = self.safe_divide_percentage(h, h + m + fa)
                    except Exception, e:
                        logging.warning('Scores unable to be calculated for %s%s | ' %(subsector, lead_time) + str(e) + '\n')
                        print 'Scores unable to be calculated for %s%s | ' %(subsector, lead_time)  + str(e)
                    else:
                        writer.writerow([lead_time, subsector, cr, h, m, fa, a, pod, far, csi])

    def assess_combined(self):
        '''
        Assesses forecast against all observations within each forecast interval block
        '''
        forecasts_filename = 'FIRSubsectors_Forecasts_Combined.csv' %self.yyyymm
        observations_filename = 'FIRSubsectors_Observations_Combined.csv' %self.yyyymm
        forecasts_filepath = os.path.join(self.inputpath, forecasts_filename)
        observations_filepath = os.path.join(self.inputpath, observations_filename) 
        try:
            forecasts_df = pd.read_csv(forecasts_filepath)
            observations_df = pd.read_csv(observations_filepath)
        except Exception, e:
            logging.warning(forecasts_filename + ' not assessed | ' + str(e) + '\n')
            print forecasts_filename + ' not assessed | ' + str(e)
        else:
            for row in forecasts_df.iterrows():
                subsector = row[1]['subsector']
                date_time = row[1]['date_time']
                duration = row[1]['duration']
                issue_date_time = row[1]['issue_date_time']
                lead_time = row[1]['lead_time']
                forecasts_category = row[1]['category']
                date_time_end = (dt.datetime.strptime(date_time, '%Y%m%d %H:%M') + dt.timedelta(hours = duration)).strftime('%Y%m%d %H:%M')
                observations_category = observations_df.loc[(observations_df['date_time']>= date_time) & (observations_df['date_time']<= date_time_end)][subsector].max()
                missing_observations = len(observations_df.loc[(observations_df['date_time']>= date_time) & (observations_df['date_time']<= date_time_end) & (observations_df[subsector] == -9999)])
                print date_time
                try:
                    if observations_category < 0:
                        cr, h, m, fa = 0, 0, 0, 0
                    elif missing_observations >= 3 and duration == 1:
                        cr, h, m, fa = 0, 0, 0, 0
                        observations_category = -8888
                    elif missing_observations >= 9 and duration == 3:
                        cr, h, m, fa = 0, 0, 0, 0
                        observations_category = -8888
                    else:
                        cr, h, m, fa = self.assessment_matrix(forecasts_category, observations_category)
                except Exception, e:
                    logging.warning(date_time + ' not assessed | ' + str(e) + '\n')
                    print date_time + ' not assessed | ' + str(e)
                else:
                    self.assessment.append({'date_time': date_time, 'issue_date_time': issue_date_time, 'subsector': subsector, 'lead_time': lead_time, 'forecast_category': forecasts_category, 'observations_category': observations_category, 'cr': cr, 'h': h, 'm': m, 'fa': fa})

    def calculate_combined(self):
        '''
        Calculates scores and outputs the results in a CSV file
        '''
        self.assessment_df = pd.DataFrame(self.assessment,columns = ['date_time', 'issue_date_time', 'subsector', 'lead_time', 'forecast_category', 'observations_category', 'cr', 'h', 'm', 'fa'])
        outputfilename_1 = 'FIRSubsectors_Assessments_Combined.csv'
        outputfilepath_1 = os.path.join(self.outputpath, outputfilename_1)
        outputfilename_2 = 'FIRSubsectors_Scores_Combined.csv'
        outputfilepath_2 = os.path.join(self.outputpath, outputfilename_2)
        self.assessment_df.to_csv(outputfilepath_1)
        with open(outputfilepath_2, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([''])
            writer.writerow(['SUMMARY'])
            writer.writerow([''])
            try:
                total_cr = self.assessment_df['cr'].sum()
                total_h = self.assessment_df['h'].sum()
                total_fa = self.assessment_df['fa'].sum()
                total_m = self.assessment_df['m'].sum()
                total_a = self.safe_divide_percentage(total_h + total_cr, total_h + total_cr + total_m + total_fa)
                total_pod = self.safe_divide_percentage(total_h, total_h + total_m)
                total_far = self.safe_divide_percentage(total_fa, total_h + total_fa)
                total_csi = self.safe_divide_percentage(total_h, total_h + total_m + total_fa)
            except Exception, e:
                logging.warning('Scores unable to be calculated | ' + str(e) + '\n')
                print 'Scores unable to be calculated | ' + str(e)
            else:
                writer.writerow(['total correct rejections', total_cr])
                writer.writerow(['total hits', total_h])
                writer.writerow(['total misses', total_m])
                writer.writerow(['total false alarms', total_fa])
                writer.writerow(['accuracy', total_a])
                writer.writerow(['probablility of detection', total_pod])
                writer.writerow(['false alarm ratio', total_far])
                writer.writerow(['critical success index', total_csi])
                writer.writerow([''])
            writer.writerow(['DETAILS'])
            writer.writerow([''])
            writer.writerow(['subsector', 'cr', 'h', 'm', 'fa', 'a', 'pod', 'far', 'csi']) 
            for subsector in sorted(self.assessment_df['subsector'].unique()):
                try:
                    cr = self.assessment_df[self.assessment_df['subsector'] == subsector]['cr'].sum()
                    h = self.assessment_df[self.assessment_df['subsector'] == subsector]['h'].sum()
                    m = self.assessment_df[self.assessment_df['subsector'] == subsector]['m'].sum()
                    fa = self.assessment_df[self.assessment_df['subsector'] == subsector]['fa'].sum()
                    a = self.safe_divide_percentage(h + cr, h + cr + m + fa)
                    pod = self.safe_divide_percentage(h, h + m)
                    far = self.safe_divide_percentage(fa, h + fa)
                    csi = self.safe_divide_percentage(h, h + m + fa)
                except Exception, e:
                    logging.warning('Scores unable to be calculated for %s | ' %subsector + str(e) + '\n')
                    print 'Scores unable to be calculated for %s | ' %subsector  + str(e)
                else:
                    writer.writerow([subsector, cr, h, m, fa, a, pod, far, csi])
            writer.writerow([''])
            writer.writerow(['lead_time', 'cr', 'h', 'm', 'fa', 'a', 'pod', 'far', 'csi'])    
            for lead_time in sorted(self.assessment_df['lead_time'].unique()):
                try:
                    cr = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['cr'].sum()
                    h = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['h'].sum()
                    m = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['m'].sum()
                    fa = self.assessment_df[self.assessment_df['lead_time'] == lead_time]['fa'].sum()
                    a = self.safe_divide_percentage(h + cr, h + cr + m + fa)
                    pod = self.safe_divide_percentage(h, h + m)
                    far = self.safe_divide_percentage(fa, h + fa)
                    csi = self.safe_divide_percentage(h, h + m + fa)
                except Exception, e:
                    logging.warning('Scores unable to be calculated for %s| ' %lead_time + str(e) + '\n')
                    print 'Scores unable to be calculated for %s | ' %lead_time  + str(e)
                else:
                    writer.writerow([lead_time, cr, h, m, fa, a, pod, far, csi])
            writer.writerow([''])
            writer.writerow(['lead_time', 'subsector', 'cr', 'h', 'm', 'fa', 'a', 'pod', 'far', 'csi'])
            for lead_time in sorted(self.assessment_df['lead_time'].unique()):
                for subsector in sorted(self.assessment_df[self.assessment_df['lead_time'] == lead_time]['subsector'].unique()):
                    try:
                        cr = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['cr'].sum()
                        h = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['h'].sum()
                        m = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['m'].sum()
                        fa = self.assessment_df[(self.assessment_df['subsector'] == subsector) & (self.assessment_df['lead_time'] == lead_time)]['fa'].sum()
                        a = self.safe_divide_percentage(h + cr, h + cr + m + fa)
                        pod = self.safe_divide_percentage(h, h + m)
                        far = self.safe_divide_percentage(fa, h + fa)
                        csi = self.safe_divide_percentage(h, h + m + fa)
                    except Exception, e:
                        logging.warning('Scores unable to be calculated for %s%s | ' %(subsector, lead_time) + str(e) + '\n')
                        print 'Scores unable to be calculated for %s%s | ' %(subsector, lead_time)  + str(e)
                    else:
                        writer.writerow([lead_time, subsector, cr, h, m, fa, a, pod, far, csi])
                    
##################################################################################################################################################################################################                
#
#   Not in use
#
#            writer.writerow([''])
#            writer.writerow(['lead_time', 'accuracy', 'probability of detection', 'false alarm ratio', 'critical success ratio'])
#            for lead_time in range(int(1 + self.assessment_df['lead_time'].max())):
#                try:
#                    lead_time_df = self.assessment_df[self.assessment_df['lead_time'] == lead_time]
#                    a = (lead_time_df['cr'].sum() + lead_time_df['h'].sum())/float(lead_time_df['cr'].sum() + lead_time_df['h'].sum() + lead_time_df['m'].sum() + lead_time_df['fa'].sum())
#                    pod = lead_time_df['h'].sum()/float(lead_time_df['h'].sum() + lead_time_df['m'].sum())
#                    far = lead_time_df['fa'].sum()/float(lead_time_df['h'].sum() + lead_time_df['fa'].sum())
#                    csi = lead_time_df['h'].sum()/float(lead_time_df['h'].sum() + lead_time_df['m'].sum() + lead_time_df['fa'].sum())
#                except Exception, e:
#                    print str(e)
#                else:
#                    writer.writerow([lead_time, a, pod, far, csi])
#            writer.writerow([''])
#            writer.writerow(['subsector', 'accuracy', 'probability of detection', 'false alarm ratio', 'critical success ratio'])
#            for subsector in self.assessment_df['subsector'].unique():
#                try:
#                    subsector_df = self.assessment_df[self.assessment_df['subsector'] == lead_time]
#                    a = (subsector_df['cr'].sum() + subsector_df['h'].sum())/float(subsector_df['cr'].sum() + subsector_df['h'].sum() + subsector_df['m'].sum() + subsector_df['fa'].sum())
#                    pod = subsector_df['h'].sum()/float(subsector_df['h'].sum() + subsector_df['m'].sum())
#                    far = subsector_df['fa'].sum()/float(subsector_df['h'].sum() + subsector_df['fa'].sum())
#                    csi = subsector_df['h'].sum()/float(subsector_df['h'].sum() + subsector_df['m'].sum() + subsector_df['fa'].sum())
#                except Exception, e:
#                    print str(e)
#                else:
#                    writer.writerow([subsector, a, pod, far, csi])
#
##################################################################################################################################################################################################


#inputpath = r'D:\SatTS\FIRSubsectors_Evaluation\Outputs'
#outputpath = r'D:\SatTS\FIRSubsectors_Evaluation\Outputs'
#yyyymm = 201807
#
#a = firsubsectors_assessment(201807, inputpath, outputpath)
#a.assess()
#a.calculate()