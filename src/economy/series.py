from unicodedata import name

import pandas as pd
import datamgmt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

db_obj = datamgmt.admin.Database('', [])


class Data:
    def __init__(self):
        
        self.fred_series = {'PCE':'pce', 
                            'DFXARC1M027SBEA':'food_pce',
                            'DNRGRC1M027SBEA':'energy_pce',
                            'DSPI':'disposable_income',
                            'B069RC1':'personal_interest', 
                            'DSPIC96':'real_disposable_income',
                            'USREC':'recession', 
                            'GDP':'gdp', 
                            'DGS10':'DGS10',
                            'DGS2':'DGS2', 
                            'FEDFUNDS':'FEDFUNDS', 
                            'CPIAUCSL':'CPIAUCSL'}
        
        self.db_series = {'ismmfg':{'date': ['date', 'date'],
                                    'index': ['ism_mfg_index','ISM Manufacturing PMI'], 
                                    'new_orders':['ism_mfg_new_orders','ISM Manufacturing New Orders Index'], 
                                    'prices': ['ism_mfg_prices', 'ISM Manufacturing Prices Index'], 
                                    'employment': ['ism_mfg_employment', 'ISM Manufacturing Employment Index']}}

        self.get_data()
        self.get_meta()
        self.CFCF()
        self.yield_curve()


    #ALL CALCULATED METRICS GO HERE
    def CFCF(self):
        self.data_['food_to_income'] = self.data_['food_pce'] / self.data_['disposable_income']
        self.data_['energy_to_income'] = self.data_['energy_pce'] / self.data_['disposable_income']
        self.data_['interest_to_income'] = self.data_['personal_interest'] / self.data_['disposable_income']

        #CFCF
        self.data_['CFCF'] = 1 - self.data_['food_to_income'] - self.data_['energy_to_income'] - self.data_['interest_to_income']

        #Add meta data for calculated metrics
        meta = pd.DataFrame(columns=self.series_meta.columns)
        meta.loc['food_to_income'] = ['Food to Income Ratio', self.series_meta.loc['DFXARC1M027SBEA', 'last_observation'], 'Monthly', '', 'Calculated as food PCE divided by disposable income', '', '', '']
        meta.loc['energy_to_income'] = ['Energy to Income Ratio', self.series_meta.loc['DNRGRC1M027SBEA', 'last_observation'], 'Monthly', '', 'Calculated as energy PCE divided by disposable income', '', '', '']
        meta.loc['interest_to_income'] = ['Interest to Income Ratio', self.series_meta.loc['B069RC1', 'last_observation'], 'Monthly', '', 'Calculated as personal interest divided by disposable income', '', '', '']
        meta.loc['CFCF'] = ['Consumer Free Cash Flow', self.series_meta.loc['PCE', 'last_observation'], 'Monthly', '', 'Calculated as 1 minus the sum of food to income, energy to income, and interest to income', '', '', ''] 

        self.series_meta = pd.concat([self.series_meta, meta])

        return True
    
    def yield_curve(self):
        self.data_['yield_curve'] = self.data_['DGS10'] - self.data_['DGS2']

        #Add meta data for calculated metric
        self.series_meta.loc['yield_curve'] = ['Yield Curve Spread', self.series_meta.loc['DGS10', 'last_observation'], 'Monthly', '', 'Calculated as the 10-year UST yield minus the 2-year UST yield', '', '', '']
        return True

    def get_meta(self):
        series_meta = datamgmt.fred.SeriesMeta(list(self.fred_series.keys())).data()
        series_release = datamgmt.fred.SeriesRelease(list(self.fred_series.keys())).data()

        series_meta = series_meta[['id', 'title', 'observation_end', 'frequency', 'last_updated', 'notes']].copy()
        series_meta.columns = ['series_id', 'title', 'last_observation', 'frequency', 'last_updated','notes']

        series_release = series_release[['series_id', 'name', 'link', 'notes']].copy()
        series_release.columns = ['series_id', 'release_name', 'release_link', 'release_notes']

        self.series_meta = pd.merge(series_meta, series_release, on='series_id', how='left')

        i=0
        for table in self.db_series.keys():
            list_of_series = [x for x in self.db_series[table].keys() if  "date" not in x]
            for col in list_of_series:
                self.series_meta.loc[len(series_meta)+i] = [self.db_series[table][col][0], self.db_series[table][col][1], self.data_.index[-1], 'varies', '', 'Internal series from database table ' + table, '', '', '']
                i+=1 

        self.series_meta.set_index('series_id', inplace=True)

        return self.series_meta

    def get_data(self):
        
        #GET ALL RAW DATA FROM INTERNAL AND EXTERNAL SOURCES, MERGE, AND CLEAN
        #get external data
        api_obj = datamgmt.fred.Observations(list(self.fred_series.keys()))
        api_data = api_obj.data()
        api_data = api_data.groupby(['id', 'date'])['value'].last().unstack('id')
        api_data.columns = [self.fred_series[col] for col in api_data.columns]
        api_data.index = pd.to_datetime(api_data.index)
        
        #get internal data
        db_data_list = []
        for table in self.db_series.keys():

            series = list(self.db_series[table].keys())
            cols = ', '.join(series[:-1]) +', ' + series[-1]

            with db_obj.engine().connect() as conn:
                query = f"SELECT {cols} FROM {table}"
                db_data = pd.read_sql(query, conn)

            db_data.columns = [self.db_series[table][col][0] for col in db_data.columns]    
            db_data.set_index('date', inplace=True)
            db_data.index = pd.to_datetime(db_data.index)
            db_data_list.append(db_data)

        db_data = pd.concat(db_data_list, axis=1)

        data = pd.merge(api_data, db_data, left_index=True, right_index=True, how='outer')

        self.data_ = data


        return data

class Transformations:
    def __init__(self):
        self.transformation_mapping = { '':self.default_transform,
                                        'yoy':self.m_yoy}

    def m_yoy(self, col):
        
        return self.data_[col].pct_change(12) * 100


    def default_transform(self, col):
        return self.data_[col]

#Object to be built for each analysis
#Its constructed with a dictionary of series and attributes:
#{econ_series: [transformation, axis]}


class Series(Transformations):
    def __init__(self, data, name:str, econ_series:dict={}):

        self.all_data = data
        self.name = name
        self.econ_series = econ_series


        self.parse_series()
        self.clean_data()
        #self.data_ = data.data_[self.series].dropna(subset=self.axis['main'])
        self.series_meta = data.series_meta.loc[self.series]
        self.recession = data.data_.dropna(subset=self.axis['main'])['recession'].ffill()  

        Transformations.__init__(self)
        self.transform()  
    
    def parse_series(self):

        #Assign series to main or sub axis based on user input in econ_series dict
        axis = {'main':[]}

        for series in self.econ_series.keys():
            if self.econ_series[series][-1] == 'main':
                axis['main'].append(series)
            elif self.econ_series[series][-1] not in axis.keys():
                axis[self.econ_series[series][-1]] = [series]
            else:
                axis[self.econ_series[series][-1]].append(series)

        self.axis = axis

        #Get list of series
        self.series = list(self.econ_series.keys())

        #Get all transformations for series
        self.transformations = dict(zip(self.series, [self.econ_series[series][0] for series in self.econ_series.keys()]))



        return True
    
    def clean_data(self):
        data = self.all_data.data_[self.series]
        for col in data.columns:
            if self.econ_series[col][1] != 'main':
                data[col] = data[col].ffill()
            else:
                continue
        
        data = data.dropna(subset=self.axis['main'])
        self.data_ = data
        return True
    
    def transform(self):
        for series in self.series:
            transformation = self.transformations[series]
            self.data_[series] = self.transformation_mapping[transformation](series)
        
        return True

    def plot(self):
        data = self.data_

        recession = self.recession

        axis = self.axis
        subplots = [x for x in axis.keys() if 'sub' in x]
        rows = 1 + len(subplots)

        # Identify transitions
        diff = recession.astype(int).diff()
        recession_starts = recession.index[diff == 1].tolist()
        recession_ends = recession.index[diff == -1].tolist()

        # Handle edge cases for start/end of series
        if recession.iloc[0] == 1:
            recession_starts.insert(0, data.index[0])
        if recession.iloc[-1] == 1:
            recession_ends.append(data.index[-1])

        # --- PLOTTING ---
        specs = [[{"secondary_y": True}]]
        for _ in range(len(subplots)):
            specs.append([{'secondary_y':False}])

        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.05, specs=specs)

        for i, name in enumerate(axis['main']):
            is_secondary = i > 0
            series_name = f'{self.series_meta.loc[name, 'title']} ({self.econ_series[name][0]})'
            fig.add_trace(go.Scatter(x=data.index, y=data[name], name=series_name), row=1, col=1, secondary_y=is_secondary)
        
        for subplot in subplots:
            for x in axis[subplot]:
                series_name = f'{self.series_meta.loc[x, 'title']} ({self.econ_series[x][0]})'
                fig.add_trace(go.Scatter(x=data.index, y=data[x], name=series_name), row=subplots.index(subplot)+2, col=1)


        # Add the shaded areas
        for start, end in zip(recession_starts, recession_ends):
            fig.add_vrect(
                x0=start, 
                x1=end,
                fillcolor="red",   # TEMPORARY: Use red to confirm they are drawing
                opacity=0.2,       # Low opacity so it doesn't block lines
                layer="below",     # Put behind the lines
                line_width=0
            )


        fig.update_layout(
            title = self.name, 
            legend=dict(
            orientation="h",      # Horizontal orientation
            yanchor="bottom",     # Anchor the bottom of the legend
            y=-0.2,               # Position it below the x-axis (negative value)
            xanchor="center",     # Center the legend horizontally
            x=0.5),   
            #height=800, 
            #width=1200, 
            template="plotly_white", hovermode="x")

        return fig
    

#Initialize data object    
data_obj = Data()

#Add preset objects for commonly used series (CFCF, ISM, etc)

#Settings for analysis on consumer free cash flow and its components, with transformations and axis assignments
cfcf_settings = {
                'CFCF':['yoy', 'main'], 
                'food_to_income':['yoy', 'sub'],
                'interest_to_income':['yoy', 'sub'],
                'energy_to_income':['yoy', 'sub']
                }

#Settings for analysis on ISM manufacturing PMI and its components, with transformations and axis assignments
ismfg_settings = {
                'ism_mfg_new_orders':['', 'main'], 
                'ism_mfg_employment':['', 'sub'],
                'ism_mfg_prices':['', 'sub'],
                'ism_mfg_index':['', 'sub']
                }

#Settings for analysis comparing ISM manufacturing PMI to consumer free cash flow, with transformations and axis assignments
ismcf_settings = ismfg_settings.copy()
ismcf_settings['CFCF'] = ['yoy', 'main']
ismcf_settings['food_to_income'] = ['yoy', 'sub1']
ismcf_settings['interest_to_income'] = ['yoy', 'sub1']
ismcf_settings['energy_to_income'] = ['yoy', 'sub1']

#Settings for analysis on yield curve and its components, with transformations and axis assignments
yield_curve_settings = {
                'yield_curve':['', 'main'], 
                'DGS10':['', 'sub'],
                'DGS2':['', 'sub'], 
                'FEDFUNDS':['', 'sub']
                }

cpi_settings = {
                'CPIAUCSL':['yoy', 'main'], 
                }


cfcf = Series(data_obj, name='Consumer Free Cash Flow', econ_series=cfcf_settings)
ismmfg = Series(data_obj, name='ISM Manufacturing PMI', econ_series=ismfg_settings)
ismcf = Series(data_obj, name='ISM Manufacturing PMI vs. Consumer Free Cash Flow', econ_series=ismcf_settings)
yield_curve = Series(data_obj, name='Yield Curve Analysis', econ_series=yield_curve_settings)
cpi = Series(data_obj, name='CPI', econ_series=cpi_settings)