# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 11:59:15 2018

@author: TYF

This is the main script to evaluate FIR Subsector forecasts for a month
"""

from firsubsectors_forecasts import firsubsectors_forecasts
from firsubsectors_observations import firsubsectors_observations
from firsubsectors_assessment import firsubsectors_assessment
import datetime as dt
import os
import logging

###############################################################################
# User defined parameters                                                     #
#                                                                             #   
# yyyymm:                 evaluation year and month in integer format         #
# observations_inputpath: folder of QGIS-processed observations CSV files     #
# forecasts_inputpath:    folder of  forecasts XML files                      #
# output_path:            folder to contain the processed observations and    #
#                         forecasts CSV files and scores of the evaluation    #
#                                                                             #
###############################################################################

#==============================================================================
yyyymm = 202010
observations_inputpath = r'C:\TYF\FIRSubsectors_Evaluation\Observations\Observations_202010'
forecasts_inputpath =  r'L:\subsectorforecast_archive'
#forecasts_inputpath =  r'C:\TYF\FIRSubsectors_Evaluation\SINGV\Fw__SINGV_forecasts_of_storm_coverage_over_FIR_for_September_2020'
#outputpath = r'C:\TYF\FIRSubsectors_Evaluation\Outputs'
outputpath = r'C:\TYF\FIRSubsectors_Evaluation\Outputs'
#==============================================================================

class firsubsectors_evaluation:
    def __init__(self, yyyymm, observations_inputpath, forecasts_inputpath, outputpath):
        '''
        Initiates an instance for evaluation
        '''
        self.yyyymm = yyyymm
        self.observations_inputpath = observations_inputpath
        self.forecasts_inputpath = forecasts_inputpath
        self.outputpath = outputpath
        
    def evaluate(self):
        '''
        Executes evaluation by creating relevant instances and calling their methods
        '''
        log_filename = os.path.join(self.outputpath, 'FIRSubsectors_Evaluation_Log_%s.log' %self.yyyymm)
        logging.basicConfig(filename=log_filename, format='%(asctime)s ~%(levelname)s : %(message)s', level=logging.INFO)
        logging.info('Evaluation for FIR Subsector Forecasts for %s starts\n' %self.yyyymm)
        forecasts = firsubsectors_forecasts(self.yyyymm, self.forecasts_inputpath, self.outputpath)
        forecasts.output_forecasts()
        observations = firsubsectors_observations(self.yyyymm, self.observations_inputpath, self.outputpath)
        observations.consolidate()
        observations.output_observations()
        assessment = firsubsectors_assessment(self.yyyymm, self.outputpath, self.outputpath)
        assessment.assess()
        assessment.calculate()

    def evaluate_combined(self):
        '''
        Executes evaluation by creating relevant instances and calling their methods
        '''
        log_filename = os.path.join(self.outputpath, 'FIRSubsectors_Evaluation_Log_Combined.log' %self.yyyymm)
        logging.basicConfig(filename=log_filename, format='%(asctime)s ~%(levelname)s : %(message)s', level=logging.INFO)
        logging.info('Evaluation for FIR Subsector Forecasts for Combined starts\n' %self.yyyymm)
        forecasts = firsubsectors_forecasts(self.yyyymm, self.forecasts_inputpath, self.outputpath)
        forecasts.output_forecasts_combined()
        observations = firsubsectors_observations(self.yyyymm, self.observations_inputpath, self.outputpath)
        observations.consolidate_combined()
        observations.output_observations_combined()
        assessment = firsubsectors_assessment(self.yyyymm, self.outputpath, self.outputpath)
        assessment.assess_combined()
        assessment.calculate_combined()
        
evaluation = firsubsectors_evaluation(yyyymm, observations_inputpath, forecasts_inputpath, outputpath)
evaluation.evaluate()


