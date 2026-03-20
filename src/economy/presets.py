from . import datamgmt

#PRESET SETTINGS
CFCF = {
        'name':'Consumer Free Cash Flow',
        'description':'''YOY change in "Consumer Free Cash Flow (CFCF)" calculated as = 1 - Food to Income Ratio - Energy to Income Ratio - Interest to Income Ratio; 
                        Supporting charts reflect YOY changes of components to the CFCF''',
        'code':'CFCF',
        'settings': {
                    'C-CFCF':[['yoy'], 'main', 1], 
                    'C-FOODTOINC':[['yoy'], 'sub', 0],
                    'C-ENETOINC':[['yoy'], 'sub', 0], 
                    'C-INTTOINC':[['yoy'], 'sub', 0]
                    }
        }

ISMVCFCF = {
        'name':'ISM New Orders vs. Consumer Free Cash Flow',
        'description': '''Comparison between ISM Manufacturing PMI and YOY change in "Consumer Free Cash Flow (CFCF)" calculated as = 1 - Food to Income Ratio - Energy to Income Ratio - Interest to Income Ratio;
                       Supporting charts reflect YOY changes of components to the CFCF as well as components to ISM Manufacturing PMI''', 
        'code':'ISMVCFCF',
        'settings': {
                    'C-CFCF':[['yoy'], 'main', 1],
                    'ISMMFGNEW':[[''], 'main', 1],  
                    'C-FOODTOINC':[['yoy'], 'sub', 0],
                    'C-ENETOINC':[['yoy'], 'sub', 0], 
                    'C-INTTOINC':[['yoy'], 'sub', 0], 
                    'ISMMFGPRICE':[[''], 'sub1', 1], 
                    'ISMMFGEMP':[[''], 'sub1', 1],
                    'ISMMFGINDX':[[''], 'sub1', 1],
                    }
        }

TWOTOTEN = {
        'name':'UST 2Y to 10Y Spread',
        'description':'''Spread between 10 Year US Treasury and 2 Year US Treasury calculated as = 10YUST - 2YUST''',
        'code':'TWOTOTEN',
        'settings': {
                    'C-TWOTOTEN':[[''], 'main', 1], 
                    }
        }

TWOTOTENVISM = {
        'name':'UST 2Y to 10Y Spread vs. ISM Manufacturing PMI',
        'description':'''Comparison between ISM Manufacturing PMI and spread between 10 Year US Treasury and 2 Year US Treasury calculated as = 10YUST - 2YUST''',
        'code':'TWOTOTENVISM',
        'settings': {
                    'ISMMFGNEW':[[''], 'main', 1],  
                    'C-TWOTOTEN':[[''], 'main', 1] 
                    }
        }

#All Models
MODELS = [
                CFCF,
                ISMVCFCF,
                TWOTOTEN
        ]