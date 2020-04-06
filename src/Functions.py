# COVID-19 infections per country
# Copyright 2020 Denis Meyer

# Functions

import logging
import io
import requests
import os
import datetime
import random

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import scipy.optimize
import numpy as np

from heapq import nlargest

class Functions():

    def initialize_logger(self, loglevel, frmt, datefmt):
        '''Initializes the logger

        :param loglevel: The log level
        :param frmt: The log format
        :param datefmt: The date format
        '''
        logging.basicConfig(level=loglevel,
                            format=frmt,
                            datefmt=datefmt)

    def download_csv_data(self, url):
        '''Downloads the data

        :param url: The data source URL
        :return: CSV data
        '''
        if not url:
            return None

        s = requests.get(url).content
        return pd.read_csv(io.StringIO(s.decode('utf-8')))

    def get_data(self, dir_csv, csv_subpath, filename_csv, url, force_refresh_data=False):
        '''Retrieves the data, either from file or download

        :param dir_csv: The CSV directory
        :param csv_subpath: The CSV sub-directory
        :param filename_csv: The CSV filename
        :param url: The URL
        :param force_refresh_data: Boolean whether to force refreshing the data
        :return: Dataframe
        '''
        df = None

        path_data = os.path.join(dir_csv, csv_subpath)
        if not os.path.exists(path_data):
            os.makedirs(path_data)
        csv_file = os.path.join(path_data, filename_csv)

        file_loaded = False
        try:
            if not force_refresh_data:
                logging.info('Not force refreshing data')
                logging.info('Trying to load from file "{}"'.format(csv_file))
                df = pd.read_csv('{}'.format(csv_file), encoding='utf-8')
                file_loaded = True
                logging.info('Successfully loaded data from file "{}"'.format(csv_file))
            else:
                logging.info('Force refreshing data')
        except FileNotFoundError:
            df = None
        if not file_loaded:
            logging.info('Downloading fresh data from "{}"...'.format(url))
            df = download_csv_data(url)
            logging.info('Trying to save to file "{}"'.format(csv_file))
            df.to_csv('{}'.format(csv_file), encoding='utf-8', index=False)
            logging.info('Successfully saved to file "{}"'.format(csv_file))

        return df

    def _get_clean_image_name(self, name):
        '''Returns a clean image name

        :param name: The image name
        :return: Cleaned image name
        '''
        return name.replace(',', '-').replace(' ', '')

    def save_plot(self, curr_dir, fig, path, date, name):
        '''Saves the plot of the fig to "<current_dir>/<name>"

        :param curr_dir: The directory
        :param fig: The figure
        :param path: The image path
        :param date: The date
        :param name: The name of the image
        :return: True if successfully saved, False else
        '''
        try:
            path_data = os.path.join(curr_dir, path if path else 'images', str(date.date()) if date else 'unknown')
            if not os.path.exists(path_data):
                os.makedirs(path_data)
            full_path = os.path.join(path_data, self._get_clean_image_name(name))
            logging.info('Saving plot to "{}"'.format(full_path))
            fig.savefig(full_path)
            return True
        except Exception as e:
            logging.info('Could not save plot to file "{}" in path "{}": {}'.format(name, path, e))
            return False

    def fit(self, x, a, b, c=1.0):
        '''Curve fitting fitting function

        :param x: x
        :param a: a
        :param b: b
        :param c: c
        :return: Function applied to parameters
        '''
        return np.exp(a + b * x)

    def sigma(self, y):
        '''Curve fitting error function

        :param y: y
        :return: Error for y
        '''
        return np.sqrt(y)

    def get_cmap(self, n, name='hsv'):
        '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct RGB color.
        The keyword argument name must be a standard mpl colormap name.

        :param n: Index
        :param name: standard mpl colormap name
        :return: Colormap function
        '''
        return plt.cm.get_cmap(name, n)
