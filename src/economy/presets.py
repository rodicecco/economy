from . import datamgmt

#PRESET SETTINGS
CFCF = {
        'name':'Consumer Free Cash Flow',
        'code':'CFCF',
        'settings': {
                    'C-CFCF':['yoy', 'main', 1], 
                    'C-FOODTOINC':['yoy', 'sub', 0],
                    'C-ENETOINC':['yoy', 'sub', 0], 
                    'C-INTTOINC':['yoy', 'sub', 0]
                    }
        }

ISMVCFCF = {
        'name':'ISM New Orders vs. Consumer Free Cash Flow',
        'code':'ISMVCFCF',
        'settings': {
                    'C-CFCF':['yoy', 'main', 1],
                    'ISMMFGNEW':['yoy', 'main', 1],  
                    'C-FOODTOINC':['yoy', 'sub', 0],
                    'C-ENETOINC':['yoy', 'sub', 0], 
                    'C-INTTOINC':['yoy', 'sub', 0], 
                    'ISMMFGPRICE':['yoy', 'sub1', 1], 
                    'ISMMFGEMP':['yoy', 'sub1', 1],
                    'ISMMFGINDX':['yoy', 'sub1', 1],
                    }
        }

TWOTOTEN = {
        'name':'UST 2Y to 10Y Spread',
        'code':'TWOTOTEN',
        'settings': {
                    'C-TWOTOTEN':['', 'main', 1], 
                    }
        }

TWOTOTENVISM = {
        'name':'UST 2Y to 10Y Spread vs. ISM Manufacturing PMI',
        'code':'TWOTOTENVISM',
        'settings': {
                    'ISMMFGNEW':['', 'main', 1],  
                    'C-TWOTOTEN':['', 'main', 1] 
                    }
        }

#All Models
MODELS = [
                CFCF,
                ISMVCFCF,
                TWOTOTEN
        ]