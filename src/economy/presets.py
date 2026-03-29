from . import datamgmt

#FINANCIAL SETTINGS
FINANCIAL_SETTINGS = {'GSPC.INDX':[['yoy'], 'finc', 0, 1],
                      'BCOMCL.INDX':[[''], 'finc', 0, 1]}

#PRESET SETTINGS

CFCF = {
        'name':'Consumer Free Cash Flow',
        'description':'''YOY change in "Consumer Free Cash Flow (CFCF)" calculated as = 1 - Food to Income Ratio - Energy to Income Ratio - Interest to Income Ratio; 
                        Supporting charts reflect YOY changes of components to the CFCF''',
        'code':'CFCF',
        'settings': {
                    'C-CFCF':[['yoy'], 'main',0, 1], 
                    'C-FOODTOINC':[['yoy'], 'sub','', 0],
                    'C-ENETOINC':[['yoy'], 'sub','', 0], 
                    'C-INTTOINC':[['yoy'], 'sub','', 0]
                    }
        }

ENGCOST = {
        'name':'Energy Cost',
        'description':'Energy Cost',
        'code':'ENGCOST',
        'settings':{
                   'C-CFCF':[['yoy'], '',0, 1],
                   'C-ENETOINC':[['yoy'], 'main','', 0], 
                   'BCOMCL.INDX':[['yoy'], 'main','', 0],
                   
                }        
        }

ISMVCFCF = {
        'name':'ISM New Orders vs. Consumer Free Cash Flow',
        'description': '''Comparison between ISM Manufacturing PMI and YOY change in "Consumer Free Cash Flow (CFCF)" calculated as = 1 - Food to Income Ratio - Energy to Income Ratio - Interest to Income Ratio;
                       Supporting charts reflect YOY changes of components to the CFCF as well as components to ISM Manufacturing PMI''', 
        'code':'ISMVCFCF',
        'settings': {
                    'C-CFCF':[['yoy'], 'main','', 1],
                    'ISMMFGNEW':[[''], 'main',50, 1],  
                    'C-FOODTOINC':[['yoy'], 'sub','', 0],
                    'C-ENETOINC':[['yoy'], 'sub','', 0], 
                    'C-INTTOINC':[['yoy'], 'sub','', 0], 
                    'ISMMFGPRICE':[[''], 'sub1','', 1], 
                    'ISMMFGEMP':[[''], 'sub1','', 1],
                    'ISMMFGINDX':[[''], 'sub1','', 1],
                    }
        }

TWOTOTEN = {
        'name':'UST 2Y to 10Y Spread',
        'description':'''Spread between 10 Year US Treasury and 2 Year US Treasury calculated as = 10YUST - 2YUST''',
        'code':'TWOTOTEN',
        'settings': {
                    'C-TWOTOTEN':[[''], 'main',0, 1], 
                    }
        }

TWOTOTENVISM = {
        'name':'UST 2Y to 10Y Spread vs. ISM Manufacturing PMI',
        'description':'''Comparison between ISM Manufacturing PMI and spread between 10 Year US Treasury and 2 Year US Treasury calculated as = 10YUST - 2YUST''',
        'code':'TWOTOTENVISM',
        'settings': {
                    'ISMMFGNEW':[[''], 'main',50, 1],  
                    'C-TWOTOTEN':[[''], 'main','', 1] 
                    }
        }

INFLATION = {
        'name':'Consumer Price Index Inflation',
        'description':'''YOY change in CPI; periods of inflation >5% have been often followed by recessionary periods after rate hicking cycles''',
        'code':'INFLATION',
        'settings': {
                    'CPIAUCSL':[['yoy'], 'main',5, 1], 
                    'FEDFUNDS':[[''], 'main','', 1] 
                    }
        }

PARTTIME = {
        'name':'Part-time to Full-time employees',
        'description':'''YOY change in part-time to full-time employees''',
        'code':'PARTTIME',
        'settings': {
                    'C-FULLTOPART':[['yoy'], 'main','', 1], 
                    'C-FULLTIME':[['yoy'], 'sub','', 0], 
                    'C-PARTTIME':[['yoy'], 'sub','', 0]
                    }
        }


#All Models
MODELS = [
                CFCF,
                ISMVCFCF,
                TWOTOTEN
        ]