##SatTS_WxWindow_FIR=name
##satelliteimagefolder=folder
##firsubsectors=vector
##tsfirfolder=folder
##logfolder=folder
##year_month=string

import os
import logging

print os.getcwd()
logging.basicConfig(filename= logfolder + '\SatTS_Processing_FIR_%s.txt' %year_month, format='%(asctime)s ~%(levelname)s : %(message)s', level=logging.INFO)
counter = 0

for satelliteimagefilename in os.listdir(satelliteimagefolder):
    tsfir = tsfirfolder + '//' + satelliteimagefilename[:-4] + 'csv'   
    satelliteimage = os.path.join(satelliteimagefolder, satelliteimagefilename)
    try:
        outputs_QGISFIELDCALCULATOR_1=processing.runalg('qgis:fieldcalculator', firsubsectors,'SS_Area',0,15.0,5.0,True,'$area',None)
        outputs_GDALOGRCLIPRASTERBYMASKLAYER_1=processing.runalg('gdalogr:cliprasterbymasklayer', satelliteimage,firsubsectors,None,True,True,True,5,4,75.0,6.0,1.0,False,0,False,None,None)
        outputs_GDALOGRPOLYGONIZE_1=processing.runalg('gdalogr:polygonize', outputs_GDALOGRCLIPRASTERBYMASKLAYER_1['OUTPUT'],'TS',None)
        outputs_QGISUNION_1=processing.runalg('qgis:union', outputs_GDALOGRPOLYGONIZE_1['OUTPUT'],outputs_QGISFIELDCALCULATOR_1['OUTPUT_LAYER'],None)
        outputs_QGISEXTRACTBYATTRIBUTE_2=processing.runalg('qgis:extractbyattribute', outputs_QGISUNION_1['OUTPUT'],'TS',2,'200',None)
        outputs_QGISEXTRACTBYATTRIBUTE_3=processing.runalg('qgis:extractbyattribute', outputs_QGISEXTRACTBYATTRIBUTE_2['OUTPUT'],'Subsector',0,'1',None)
        outputs_QGISFIELDCALCULATOR_2=processing.runalg('qgis:fieldcalculator', outputs_QGISEXTRACTBYATTRIBUTE_3['OUTPUT'],'TS_Area',0,15.0,5.0,True,'$area',None)
        outputs_QGISFIELDCALCULATOR_3=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_2['OUTPUT_LAYER'],'TS_Percent',0,15.0,5.0,True,'TS_Area/SS_Area',None)
        outputs_QGISFIELDCALCULATOR_4=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_3['OUTPUT_LAYER'],'Sum',0,15.0,5.0,True,'sum("TS_Percent", "Sector")',None)
        outputs_GDALOGRCONVERTFORMAT_1=processing.runalg('gdalogr:convertformat', outputs_QGISFIELDCALCULATOR_4['OUTPUT_LAYER'],12,None,tsfir)
    except Exception, e:
        logging.warning(satelliteimagefilename + ' not processed | ' + str(e) + '\r\n')
        print 'WARNING: ' + satelliteimagefilename + ' not processed | ' + str(e)
        counter += 1
    else:
        print satelliteimagefilename + ' processed'
    
logging.info(str(counter))