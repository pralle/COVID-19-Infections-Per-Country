# COVID-19 infections per country
# Copyright 2020 Denis Meyer

# Settings

import logging

### Data source ###
# 2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE
# https://github.com/CSSEGISandData/COVID-19
SETTINGS_DATASOURCE = {
    'infections': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
    'deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
}

### Misc settings ###

SETTINGS = {
    # Ignores file cache if 'True', tries to load data for the current day from file cache otherwise
    'force_refresh_data': False,
    # Image path to save the created plot images to (relative to the current directory)
    'plot_image_path': 'images',
    # Directory names
    'csv_subdir_name': 'data',
    'csv_infections_subdir_name': 'infections',
    'csv_deaths_subdir_name': 'deaths',
    # README
    'generate_readme': True,
    'readme_template': 'README.md.tmpl',
    'readme': 'README.md',
    # Cache file name
    'csv_infections_filename': 'time_series_19-covid-Confirmed-{}.csv',
    'csv_deaths_filename': 'time_series_19-covid-Deaths-{}.csv',
    # Plot configuration
    'plot': {
        'size': (20, 15),
        'title': 'COVID-19 infections per country',
        'label_x': 'Date',
        'label_y': 'Nr of'
    },
    # Data source
    'datasource': {
        'infections': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
        'deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
    },
    # Logging configuration
    'logging': {
        'loglevel': logging.INFO,
        'date_format': '%d-%m-%Y %H:%M:%S',
        'format': '[%(asctime)s] [%(levelname)-5s] [%(module)-20s:%(lineno)-4s] %(message)s'
    }
}
