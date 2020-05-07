# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash_table import DataTable

import pandas as pd
import requests

import logging
import io
import requests
import os
import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import scipy.optimize
import numpy as np
from heapq import nlargest

COUNTRY_KEY = 'Country/Region'


def download_csv_data(url: str) -> pd.DataFrame:
    '''Downloads the data

    :param url: The data source URL
    '''
    if not url:
        return None

    s = requests.get(url).content
    _df = pd.read_csv(io.StringIO(s.decode('utf-8')))
    _df = _df.drop(['Province/State', 'Lat', 'Long'], axis=1)
    df_grouped_summed = _df.groupby('Country/Region').sum().reset_index()
    return df_grouped_summed


df = download_csv_data('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
all_countries_list = list(df[COUNTRY_KEY])

def getCountry(country, slice = [None,None]):
    _df = df[df[COUNTRY_KEY] == country]
    x = [datetime.datetime.strptime(d, '%m/%d/%y').date() for d in _df if d != COUNTRY_KEY]
    y = [_df[d].values[0] for d in _df if d != COUNTRY_KEY]
    return x[slice[0]:slice[1]], y[slice[0]:slice[1]]

def getDelta(list):
    return [list[i] - list[i-1] for i in range(1,len(list))]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True

def getRangeSlicer():
    dates = getCountry('Germany')[0]

    return dcc.RangeSlider(
        min=0,
        max=len(dates),
        value=[35, len(dates)],
        marks={i: {'label': str(dates[i])} for i in range(0, len(dates), 14)},
        id='slicer'
    )

def func_fit(x, a, b):
    return a + b * x

def func_plot(x, a, b):
    return np.exp(func_fit(x, a, b))

def fit(x, y, c):
    data = [d for d in zip(x,y) if d[1] > 0]
    fit_x, fit_y = zip(*data)
    params, params_cov = scipy.optimize.curve_fit(func_fit, xdata=[xx.toordinal() for xx in fit_x], ydata=np.log(fit_y))
    print(fit)
    plot_y = [func_plot(xx.toordinal(), *params) for xx in x]
    print(plot_y)
    print(params)
    return {'x': x, 'y': plot_y, 'name': '{}-fit'.format(c), 'mode': 'line'}

def toPlot(x, y, c):
    return {'x': x, 'y': y, 'name': c}#, 'mode': 'markers', 'marker': {'size': 4}}

def toDiffPlot(x, y, c):
    _x = x[1:]
    _y = getDelta(y)
    return {'x': _x, 'y': _y, 'name': c}#, 'mode': 'markers', 'marker': {'size': 4}}

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                options=[
                    {'label': c, 'value': c} for c in all_countries_list
                ],
                value=['Germany', 'Italy', 'United Kingdom'],
                multi=True,
                id='country-selector'
            ),
            getRangeSlicer()
        ], className='twelfe columns'),
    ], className='row'),
    html.Div([
        html.Div(children=[
        ], className='six columns', id='country_row_total'),
        html.Div(children=[
        ], className='six columns', id='country_row_new')
    ], className='row')
], className='ten columns offset-by-one')

@app.callback(
    [Output("country_row_new", "children")],
    [Input('country-selector', 'value'), Input('slicer', 'value')]
)
def updateGraph1(countries, slice):
    return [dcc.Graph(
        id='example-graph',
        figure={
            'data': [toDiffPlot(*getCountry(c, slice), c) for c in countries],
            'layout': {
                'title': 'Neuansteckungen'
            }
        }
    )]

@app.callback(
    [Output("country_row_total", "children")],
    [Input('country-selector', 'value'), Input('slicer', 'value')]
)
def updateGraph2(countries, slice):
    return [dcc.Graph(
        id='example-graph',
        figure={
            'data': [toPlot(*getCountry(c, slice), c) for c in countries], #+ [fit(*getCountry(c, slice), c) for c in countries],
            'layout': {
                'title': 'Alle Fälle'
            }
        }
    )]

if __name__ == "__main__":
    app.run_server(port=8053, debug=True)