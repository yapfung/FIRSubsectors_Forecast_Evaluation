# FIRSubsectors Evaluation

## Overview

This is a program to evaluate FIR Subsectors Forecast. \
The program uses both QGIS and Python scripts. \
The evalution is run on the workstation 192.168.101.39. 


## Data Flow (Simplified)

    SatTS TIFF files
            |
            |
    PY processing scripts for QGIS
            |
            |
            V
    Observations CSV files            Forecast XML files
            |                                 |
            |_________________________________|
                            |
                            |
                            V
                    Other PY scripts
                            |
                            |
                            V
            Score and other output CSV Files
            

## Input Data

| Category           | Description |
| ---                |  ------  |
| SatTS TIFF files   | 192.168.16.15:/Data90TB/general/HPC/forecast_archive/SatTS_tiff |
| Forecast XML files | \\\\192.168.5.26\Tcs\subsectorforecast_archive |


## Output Data

| Category                         | Description |
| ---                              |  ------  |
| Observations CSV files           | \\\\192.168.101.39:TYF\FIRSubsectors_Evaluation\Observations |
| Score and other output CSV files | \\\\192.168.101.39:TYF\FIRSubsectors_Evaluation\Outputs |

## Configuration

Program configuration can be found and ammended accordingly in `firsubsectors_evaluation.py`



           