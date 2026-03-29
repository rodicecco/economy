import pandas as pd
import datamgmt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

db_obj = datamgmt.admin.Database('', [])

def finc_series_meta():
    meta_columns = ['title', 'notes', 'series_id', 'name', 'link']
    meta = {'GSPC.INDX':['S&P 500', 'U.S Large Cap', 'SPY', '', ''], 
            'BCOMCL.INDX':['WTI Crude Oil', 'Crude Oil', 'BCOMCL.INDX', '', '']}
    frame = pd.DataFrame(meta).T
    frame.columns = meta_columns
    frame.index = frame.index.astype(object)
    return frame


def load_from_db(columns:list, table:str, id_driver:str, series_ids:list):
        cols_str = ', '.join(columns)
        series_ids = ', '.join([f"'{x}'" for x in series_ids])

        query = f'''SELECT {cols_str} FROM {table} WHERE {id_driver} IN ({series_ids})'''

        with db_obj.engine().connect() as conn:
            resp = pd.read_sql(query, conn)

        return resp

def load_from_api(symbols:list):
    obj = datamgmt.eod.Historical(symbols)
    data = obj.data(symbols)
    data = obj.data(symbols).groupby(['date', 'symbol'])['adjusted_close'].last().unstack('symbol')
    data.index = pd.to_datetime(data.index)
    return data

def rank_transform(df):
    """
    Ranks columns against each other for each date.
    1 is the highest value (e.g., highest GDP growth).
    """
    return df.rank(axis=1, ascending=False, method='min')

#Class for calculated metrics

class CFCF:
    
    def __init__(self):

        self.series_ids = [
                            'DFXARC1M027SBEA',                 #Food PCE
                            'DNRGRC1M027SBEA',                 #Energy PCE
                            'DSPI',                            #Disposable Income
                            'B069RC1'                          #Personal Interest
                          ]
        #Data initially empty
        self.data = None

    def calculate(self):
        #Preliminary calculations
        self.data['C-FOODTOINC'] = self.data['DFXARC1M027SBEA'] / self.data['DSPI']
        self.data['C-ENETOINC'] = self.data['DNRGRC1M027SBEA'] / self.data['DSPI']
        self.data['C-INTTOINC'] = self.data['B069RC1'] / self.data['DSPI']

        #CFCF Calculation
        self.data['C-CFCF'] = 1 - self.data['C-FOODTOINC'] - self.data['C-ENETOINC'] - self.data['C-INTTOINC']
        self.data = self.data[['C-CFCF', 'C-FOODTOINC', 'C-ENETOINC', 'C-INTTOINC']]
        
        #ID : 'title', 'notes', 'series_id', 'name', 'link'
        self.meta_index = ['C-FOODTOINC', 'C-ENETOINC', 'C-INTTOINC','C-CFCF']
        self.meta = [['Food to Income Ratio', 'Food PCE / Disposable Income', 'C-FOODTOINC', '', ''], 
                     ['Energy to Income Ratio', 'Energy PCE / Disposable Income', 'C-ENETOINC', '', ''], 
                     ['Interest to Income Ratio', 'Personal Interest / Disposable Income', 'C-INTTOINC', '', ''], 
                     ['Consumer Free Cash Flow', '1 - Food to Income Ratio - Energy to Income Ratio - Interest to Income Ratio', 'C-CFCF', '', '']]
        self.meta_columns = ['title', 'notes', 'series_id', 'name', 'link']
        self.meta_table = pd.DataFrame(self.meta,index = self.meta_index, columns=self.meta_columns)
        self.meta_table.index = self.meta_table.index.astype(object)
        
        return self.data

class YIELDCURVE:
    
    def __init__(self):

        self.series_ids = [
                            'DGS10',                            #10-Year UST Yield
                            'DGS2',                             #2-Year UST Yield
                          ]
        #Data initially empty
        self.data = None

    def calculate(self):
        #Yield Curve Calculation
        self.data['C-TWOTOTEN'] = self.data['DGS10'] - self.data['DGS2']
        self.data = self.data[['C-TWOTOTEN']]
        
        #ID : 'title', 'notes', 'series_id', 'name', 'link'
        self.meta_index = ['C-TWOTOTEN']
        self.meta = [
                        ['UST 2Y to 10Y Spread', 'UST10Y - UST2Y', 'C-TWOTOTEN', '', '']
                    ]
        
        self.meta_columns = ['title', 'notes', 'series_id', 'name', 'link']
        self.meta_table = pd.DataFrame(self.meta,index = self.meta_index, columns=self.meta_columns)
        self.meta_table.index = self.meta_table.index.astype(object)
        
        return self.data


class PARTTIME:
    
    def __init__(self):

        self.series_ids = [
                            'LNS12005977',
                            'LNS12032194',
                            'CE16OV'                             
                          ]
        #Data initially empty
        self.data = None

    def calculate(self):
        #Yield Curve Calculation
        self.data['C-PARTTIME'] = self.data['LNS12005977'] + self.data['LNS12032194']
        self.data['C-FULLTIME'] = self.data['CE16OV'] - self.data['C-PARTTIME']
        self.data['C-FULLTOPART'] = self.data['C-FULLTIME'] / self.data['C-PARTTIME']
        self.data = self.data[['C-PARTTIME', 'C-FULLTIME', 'C-FULLTOPART']]
        
        #ID : 'title', 'notes', 'series_id', 'name', 'link'
        self.meta_index = ['C-PARTTIME', 'C-FULLTIME', 'C-FULLTOPART']
        self.meta = [
                        ['Part Time Employees', 'Part-time for economic & non-economic reasons', 'C-PARTTIME', '', ''], 
                        ['Full-time employees', 'All employees excluding all part-time employees', 'C-FULLTIME', '', ''], 
                        ['Full-to-Part Ratio', 'Ratio of full-time to part-time employees', 'C-FULLTOPART', '', '']
                    ]
        
        self.meta_columns = ['title', 'notes', 'series_id', 'name', 'link']
        self.meta_table = pd.DataFrame(self.meta,index = self.meta_index, columns=self.meta_columns)
        self.meta_table.index = self.meta_table.index.astype(object)
        
        return self.data


CALCMENU = {
            'C-CFCF':CFCF, 
            'C-TWOTOTEN':YIELDCURVE, 
            'C-FULLTOPART':PARTTIME
            }

    

class EconData:
    def __init__(self, series_ids=[], financials=['SPY']):
        
        #Define data columns, table and driver
        self.data_columns = ['date', 'id', 'value']
        self.data_table = 'econ_hist'
        self.id_driver = 'id'

        #Define meta data columns, table and driver
        self.series_columns = ['id', 'title', 'notes']
        self.series_table = 'econ_series_meta'
        self.series_id_driver = 'id'

        self.release_columns = ['series_id', 'name', 'link']
        self.release_table = 'econ_series_release'
        self.release_id_driver = 'series_id'

        #Define series_ids to be pulled
        self.series_ids = series_ids
        self.financials = financials

        self.parse_series()
        self.series_ids.append('USREC')


        #Log of loaded series
        self.loaded_series = []
    
    def parse_series(self):
        series_ids = []
        calc_series = []
        for series in self.series_ids:
            if series.split('-')[0] == 'C':
                calc_series.append(series)
            else:
                series_ids.append(series)
        self.series_ids = series_ids
        self.calc_series = calc_series
        return True

    def load_data(self):
        #Load financial data from API
        finc_data = load_from_api(self.financials)

        #Load economic data from internal sources
        resp = load_from_db(self.data_columns, self.data_table, self.id_driver, self.series_ids)

        data = resp
        data = data.groupby(['date', self.id_driver]).last().unstack(self.id_driver)
        data.index = pd.to_datetime(data.index)
        data = data.droplevel(0, axis=1)

        min_date = min(data.index.min(), finc_data.index.min())
        max_date = max(data.index.max(), finc_data.index.max())
        daily_index = pd.date_range(min_date, max_date, freq='D')
        data = data.reindex(daily_index, fill_value=np.nan)

        data = data.merge(finc_data, how='left', left_index=True, right_index=True)
        data[self.financials] = data[self.financials].ffill()
        data.index.name = 'date'
        data = data.resample('MS').last()

        self.data_ = data

        return data

    def load_meta(self):
        
        resp_series = load_from_db(self.series_columns, self.series_table, self.series_id_driver, self.series_ids)
        resp_release = load_from_db(self.release_columns, self.release_table, self.release_id_driver, self.series_ids)

        series_meta = pd.merge(resp_series, resp_release, left_on='id', right_on='series_id', how='left')
        series_meta.set_index('id', inplace=True)

        finc_meta = finc_series_meta().loc[self.financials]
        series_meta = pd.concat([series_meta, finc_meta], ignore_index=False)


        self.meta_ = series_meta

        return series_meta

    def gather_calc_series(self):
        for calculation in self.calc_series:
            self.series_ids = self.series_ids + CALCMENU[calculation]().series_ids
        return True
    
    def load_calculated_series(self):
        for calculation in self.calc_series:
            obj = CALCMENU[calculation]()
            obj.data = self.data_.copy()
            calc_data = obj.calculate()
            self.data_ = self.data_.merge(calc_data, left_index=True, right_index=True, how='left')

            self.meta_ = pd.concat([self.meta_, obj.meta_table], ignore_index=False)
            setattr(self, calculation.split('-')[-1], obj)
        return True



    def load(self):
        self.gather_calc_series()
        self.load_data()
        self.load_meta()
        self.load_calculated_series()
        return True



class Transformations:
    def __init__(self):
        self.transformation_mapping = { '':self.default_transform,
                                        'yoy':self.yoy}

    def yoy(self, col):
    # Use pd.DateOffset to ensure it looks back exactly 1 year
        return self.data_[col].pct_change(freq=pd.DateOffset(years=1)) * 100


    def default_transform(self, col):
        return self.data_[col]
    
class Series(Transformations):
    def __init__(self, name:str='', description:str='', code:str='',  settings:dict={}, finc_settings:dict={}):

        self.name = name
        self.description = description
        self.code = code
        self.settings = settings
        self.finc_settings = finc_settings
        self.all_data = None

        self.parse_series()

        Transformations.__init__(self)

    def parse_series(self):
        #Assign series to main or sub axis based on user input in econ_series dict
        axis = {'main':[]}

        for series in self.settings.keys():
            if self.settings[series][1] == 'main':
                axis['main'].append(series)
            elif self.settings[series][1] not in axis.keys():
                axis[self.settings[series][1]] = [series]
            else:
                axis[self.settings[series][1]].append(series)

        self.axis = axis

        #Get list of series
        series_ids = []
        for series in self.settings.keys():
            if self.settings[series][-1] == 1:
                series_ids.append(series)
            else:
                continue

        #self.master_series = [x for x in series_ids if self.settings[x][3] == 'master']
        self.series = series_ids
        self.global_series = list(self.settings.keys())
        self.global_series = self.global_series

        self.finc_series = list(self.finc_settings.keys())

        #Get all transformations for series
        self.transformations = dict(zip(self.global_series, [self.settings[series][0] for series in self.global_series]))
        self.finc_transformations = dict(zip(self.finc_series, [self.finc_settings[series][0] for series in self.finc_series]))


        self.thresholds = dict(zip(self.global_series, [self.settings[series][2] for series in self.global_series]))

        return True
    
    def clean_data(self):

        self.series_meta = self.all_data.meta_.loc[list(set(self.global_series+self.finc_series))]
        data = self.all_data.data_[list(set(self.global_series+self.finc_series))].copy()
        #data = data.resample('ME').last()
        min_date = data[self.axis['main']].dropna().index.min()
        data = data.loc[min_date:]

        for col in self.global_series:
            if self.settings[col][1] != 'main':
                data[col] = data[col]
            else:
                continue
        
        #data = data.dropna(subset=self.axis['main'])
        self.data_ = data
        self.recession = self.all_data.data_.dropna(subset=self.axis['main'])['USREC'].ffill() 
        return True

    def transform(self):
        for series in self.global_series:
            transformation = self.transformations[series]
            for trans in transformation:
                self.data_[series] = self.transformation_mapping[trans](series)

        for series in self.finc_series:
            transformation = self.finc_transformations[series]
            for trans in transformation:
                self.data_[series] = self.transformation_mapping[trans](series)
        
        return True
    
    def load(self):
        self.clean_data()
        self.transform()

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
        #specs.append([{'secondary_y':False}])


        fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.05, specs=specs)

        for i, name in enumerate(axis['main']):
            is_secondary = i > 0
            threshold = self.thresholds[name]

            series_name = f'{self.series_meta.loc[name, 'title']} ({self.settings[name][0]})'
            fig.add_trace(go.Scatter(x=data.index, y=data[name], name=series_name), row=1, col=1, secondary_y=is_secondary)
            if threshold =='':
                continue
            else:
                fig.add_trace(go.Scatter(x=data.index, y=np.repeat(threshold, len(data.index)), opacity=0.5, showlegend=False), row=1, col=1, secondary_y=is_secondary)
        
        for subplot in subplots:
            for x in axis[subplot]:
                series_name = f'{self.series_meta.loc[x, 'title']} ({self.settings[x][0]})'
                fig.add_trace(go.Scatter(x=data.index, y=data[x], name=series_name), row=subplots.index(subplot)+2, col=1)

        
        #for x in self.finc_series:
        #    series_name = f'{self.series_meta.loc[x, "title"]} ({self.finc_settings[x][0]})'
        #    fig.add_trace(go.Scatter(x=data.index, y=data[x], name=series_name), row=rows, col=1)



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
            #title={
            #    'text': self.name,
            #    'font': {'size': 20, 'family': 'Arial, sans-serif'} # TITLE FONT
            #},
            legend=dict(
                        orientation="h",      # Horizontal orientation
                        yanchor="bottom",     # Anchor the bottom of the legend
                        y=-0.2,               # Position it below the x-axis (negative value)
                        xanchor="center",     # Center the legend horizontally
                        x=0.5, 
                        font = {'size': 12}),
            font={'family': "Arial, sans-serif", 'color': "black"},   
            margin=dict(l=10, r=10, t=10, b=10), # 't' is 50 to leave room for the title
            height = 400*rows,
            autosize=True,
            template="plotly_white", hovermode="x")

        return fig


class Models:
    def __init__(self, settings_list:list=[], finc_settings:dict={}):
        self.settings_list = settings_list
        self.finc_settings = finc_settings
    
    def initialized_models(self):

        series_ids = []
        objs = []

        for settings in self.settings_list:
            obj = Series(**settings, finc_settings=self.finc_settings)
            series_ids = series_ids + obj.series
            objs.append(obj)

        series_ids = list(set(series_ids))
        self.series_ids = series_ids

        finc_symbols = list(self.finc_settings.keys())

        data_obj = EconData(series_ids = series_ids, financials = finc_symbols)
        data_obj.load()
        self.data = data_obj

        for obj in objs:
            obj.all_data = data_obj
            obj.load()
            setattr(self, obj.code, obj)

        return True



