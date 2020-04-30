# COVID-19 infections per country
# Copyright 2020 Denis Meyer

# Plot: Curve fit specific country

import logging
import os
import datetime

import matplotlib.pyplot as plt
from heapq import nlargest
import scipy.optimize
import numpy as np

class PlotMultiCurveFitSpecificCountry():

    PLOTTING_SETTINGS = {
        # The plot name
        'plot_name': 'Multi curve fit ({}) for country "{}"',
        # Plot start day
        'start_day': 40,
        # Plot end day, use a number <= 0 to plot til last day
        'end_day': -1,
        # Boolean flag whether to plot deaths
        'plot_deaths': True,
        # The country to plot
        'country': 'Germany',
        # Plot every n-th tick
        'nth_tick': 4,
        # Fitting data
        'fits': {
            'infections': [
                {
                    'start_day': 40,
                    'end_day': 50,
                    'plot_start_day': 40,
                    'plot_end_day': 52,
                    'color': 'lightskyblue'
                },
                {
                    'start_day': 51,
                    'end_day': 58,
                    'plot_start_day': 49,
                    'plot_end_day': 64,
                    'color': 'blue'#,
                },
                {
                    'start_day': 58,
                    'end_day': 65,
                    'plot_start_day': 56,
                    'plot_end_day': 67,
                    'color': 'steelblue'
                },
                {
                    'start_day': 67,
                    'end_day': 74,
                    'plot_start_day': 65,
                    'plot_end_day': 76,
                    'color': 'slateblue'
                },
                {
                    'start_day': 78,
                    'end_day': 85,
                    'plot_start_day': 76,
                    'plot_end_day': 81,
                    'color': 'indigo'
                },
                {
                    'start_day': 83,
                    'end_day': 89,
                    'plot_start_day': 80,
                    'plot_end_day': 91,
                    'color': 'darkviolet'
                },
                {
                    'start_day': 90,
                    'end_day': 96,
                    'plot_start_day': 88,
                    'plot_end_day': -1,
                    'color': 'darkorchid'
                }
            ],
            'deaths': [
                {
                    'start_day': 51,
                    'end_day': 58,
                    'plot_start_day': 49,
                    'plot_end_day': 64,
                    'color': 'blue'#,
                },
                {
                    'start_day': 58,
                    'end_day': 65,
                    'plot_start_day': 56,
                    'plot_end_day': 67,
                    'color': 'steelblue'
                },
                {
                    'start_day': 67,
                    'end_day': 74,
                    'plot_start_day': 65,
                    'plot_end_day': 76,
                    'color': 'slateblue'
                },
                {
                    'start_day': 78,
                    'end_day': 85,
                    'plot_start_day': 76,
                    'plot_end_day': 81,
                    'color': 'indigo'
                },
                {
                    'start_day': 83,
                    'end_day': 89,
                    'plot_start_day': 80,
                    'plot_end_day': 91,
                    'color': 'darkviolet'
                },
                {
                    'start_day': 90,
                    'end_day': 96,
                    'plot_start_day': 88,
                    'plot_end_day': -1,
                    'color': 'darkorchid'
                }
            ]
        },
        # Fitting functions
        'fit_func': {
            'infections': lambda x, a, b, c: np.exp(a + b * x),
            'deaths': lambda x, a, b, c: np.exp(a + b * x)
        },
        # For debugging and parameter tweaking purposes: Activate to plot only the data in the full range
        'raw_data_only': False,
        # Boolean flag whether to plot days as x-label instead of dates
        'plot_days_as_label_x': False
    }

    def __init__(self, functions, settings, plot_settings, plotting_settings=PLOTTING_SETTINGS):
        self.functions = functions
        self.settings = settings
        self.plot_settings = plot_settings
        self.plotting_settings = plotting_settings

    def plot_infections(self, dates, df_grouped_summed, df_deaths_grouped_summed, date_first, date_last):
        plot_name = self.plotting_settings['plot_name'].format('infections', self.plotting_settings['country'])

        if not self.plot_settings['plot']['infections']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return None, None

        file_path = ''

        logging.info('Plotting "{}"'.format(plot_name))

        # Gather all countries
        all_countries_list = list(df_grouped_summed['Country/Region'])

        if self.plotting_settings['country'] in all_countries_list:
            fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

            # Infected
            df_tmp = df_grouped_summed[df_grouped_summed['Country/Region']==self.plotting_settings['country']]
            df_melted = df_tmp.melt(id_vars=df_tmp.columns.values[:1], var_name='Date', value_name='Value')

            lowest_start_day = len(df_melted.Value)
            highest_end_day = 0
            for i, data in enumerate(self.plotting_settings['fits']['infections']):
                # Validate start and end days
                day_end = data['end_day'] if (data['end_day'] > 0 and data['end_day'] < len(df_melted.Value)) else len(df_melted.Value)
                day_start = data['start_day'] if data['start_day'] > 0 and data['start_day'] < day_end else 0
                logging.info('Fitting to days [{}, {}]'.format(day_start, day_end))

                # Validate plot start and end days
                plot_day_end = data['plot_end_day'] if (data['plot_end_day'] > 0 and data['plot_end_day'] < len(df_melted.Value)) else len(df_melted.Value)
                plot_day_start = data['plot_start_day'] if data['plot_start_day'] > 0 and data['plot_start_day'] < plot_day_end else 0
                logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))
                lowest_start_day = plot_day_start if plot_day_start < lowest_start_day else lowest_start_day
                highest_end_day = plot_day_end if plot_day_end > highest_end_day else highest_end_day

                vals_x = np.linspace(0, len(df_melted.Value), num = len(df_melted.Value))[day_start:day_end]
                vals_y = list(df_melted.Value)[day_start:day_end]
                vals_sigma = [self.functions.sigma(y) for y in vals_y]

                vals_x_to_end = [t for t in range(plot_day_start, plot_day_end)]
                vals_y_to_end = list(df_melted.Value)[plot_day_start:plot_day_end]

                if not self.plotting_settings['raw_data_only']:
                    # Scipy curve fit
                    try:
                        func = self.plotting_settings['fit_func']['infections'] if 'fit_func' in self.plotting_settings else self.functions.fit
                        params, params_cov = scipy.optimize.curve_fit(func, xdata=vals_x, ydata=vals_y, sigma=vals_sigma)
                        vals_y_fit = [func(x, params[0], params[1], 0) for x in vals_x_to_end]
                        ax.plot(vals_x_to_end, vals_y_fit, '--', color=data['color'], label='Fit - days {}-{}'.format(day_start, day_end))
                    except Exception as e:
                        logging.info('Could not find curve fit: "{}"'.format(e))
                else:
                    logging.info('Just logging data')

            # Plot deaths
            if self.plotting_settings['plot_deaths']:
                # Deaths
                df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==self.plotting_settings['country']]
                df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')

                vals_x_to_end = [t for t in range(lowest_start_day, highest_end_day)]
                vals_y_deaths_to_end = list(df_deaths_melted.Value)[lowest_start_day:highest_end_day]
                ax.plot(vals_x_to_end, vals_y_deaths_to_end, '-', color='red', label='Deaths')

            # Plot data
            plot_vals_x = [t for t in range(lowest_start_day, highest_end_day)]
            plot_vals_y = list(df_melted.Value)[lowest_start_day:highest_end_day]
            ax.plot(plot_vals_x, plot_vals_y, 'o', color='green', label='Infections')

            ax.set_title('{} - {} - {}'.format(self.settings['plot']['title'], date_last.date(), plot_name), loc='center')
            ax.set_xlabel(self.settings['plot']['label_x'])
            ax.set_ylabel(self.settings['plot']['label_y'])

            logging.info('Calculating ticks for days [{}, {}]'.format(lowest_start_day, highest_end_day))
            # Calculate ticks and labels (=the dates on the x-axis)
            ticks = [t for t in range(lowest_start_day, highest_end_day)][::self.plotting_settings['nth_tick']]
            if self.plotting_settings['plot_days_as_label_x']:
                labels = [d for d in ticks]
            else:
                labels = [str((date_first + datetime.timedelta(days=d)).date()) for d in ticks]
            plt.xticks(ticks=ticks, labels=labels)

            plt.legend(loc='upper left')
            plt.show()

            if self.plot_settings['save_to_file']:
                file_path = self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format('Infections', self.plotting_settings['country']))

            plt.close(fig)
        else:
            logging.info('Could not find given country "{}"'.format(self.plotting_settings['country']))

        return file_path, plot_name

    def plot_deaths(self, dates, df_grouped_summed, df_deaths_grouped_summed, date_first, date_last):
        plot_name = self.plotting_settings['plot_name'].format('deaths', self.plotting_settings['country'])

        if not self.plot_settings['plot']['deaths']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return None, None

        file_path = ''

        logging.info('Plotting "{}"'.format(plot_name))

        # Gather all countries
        all_countries_list = list(df_grouped_summed['Country/Region'])

        if self.plotting_settings['country'] in all_countries_list:
            fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

            # Deaths
            df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==self.plotting_settings['country']]
            df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')

            lowest_start_day = len(df_deaths_melted.Value)
            highest_end_day = 0
            for i, data in enumerate(self.plotting_settings['fits']['deaths']):
                # Validate start and end days
                day_end = data['end_day'] if (data['end_day'] > 0 and data['end_day'] < len(df_deaths_melted.Value)) else len(df_deaths_melted.Value)
                day_start = data['start_day'] if data['start_day'] > 0 and data['start_day'] < day_end else 0
                logging.info('Fitting to days [{}, {}]'.format(day_start, day_end))

                # Validate plot start and end days
                plot_day_end = data['plot_end_day'] if (data['plot_end_day'] > 0 and data['plot_end_day'] < len(df_deaths_melted.Value)) else len(df_deaths_melted.Value)
                plot_day_start = data['plot_start_day'] if data['plot_start_day'] > 0 and data['plot_start_day'] < plot_day_end else 0
                logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))
                lowest_start_day = plot_day_start if plot_day_start < lowest_start_day else lowest_start_day
                highest_end_day = plot_day_end if plot_day_end > highest_end_day else highest_end_day

                vals_x = np.linspace(0, len(df_deaths_melted.Value), num = len(df_deaths_melted.Value))[day_start:day_end]
                vals_y = list(df_deaths_melted.Value)[day_start:day_end]
                vals_sigma = [self.functions.sigma(y) for y in vals_y]

                vals_x_to_end = [t for t in range(plot_day_start, plot_day_end)]
                vals_y_to_end = list(df_deaths_melted.Value)[plot_day_start:plot_day_end]

                if not self.plotting_settings['raw_data_only']:
                    # Scipy curve fit
                    try:
                        func = self.plotting_settings['fit_func']['deaths'] if 'fit_func' in self.plotting_settings else self.functions.fit
                        params, params_cov = scipy.optimize.curve_fit(func, xdata=vals_x, ydata=vals_y, sigma=vals_sigma)
                        vals_y_fit = [func(x, params[0], params[1], 0) for x in vals_x_to_end]
                        ax.plot(vals_x_to_end, vals_y_fit, '--', color=data['color'], label='Fit - days {}-{}'.format(day_start, day_end))
                    except Exception as e:
                        logging.info('Could not find curve fit: "{}"'.format(e))
                else:
                    logging.info('Just logging data')

            # Plot data
            plot_vals_x = [t for t in range(lowest_start_day, highest_end_day)]
            plot_vals_y = list(df_deaths_melted.Value)[lowest_start_day:highest_end_day]
            ax.plot(plot_vals_x, plot_vals_y, 'o', color='green', label='Infections')

            ax.set_title('{} - {} - {}'.format(self.settings['plot']['title'], date_last.date(), plot_name), loc='center')
            ax.set_xlabel(self.settings['plot']['label_x'])
            ax.set_ylabel(self.settings['plot']['label_y'])

            logging.info('Calculating ticks for days [{}, {}]'.format(lowest_start_day, highest_end_day))
            # Calculate ticks and labels (=the dates on the x-axis)
            ticks = [t for t in range(lowest_start_day, highest_end_day)][::self.plotting_settings['nth_tick']]
            if self.plotting_settings['plot_days_as_label_x']:
                labels = [d for d in ticks]
            else:
                labels = [str((date_first + datetime.timedelta(days=d)).date()) for d in ticks]
            plt.xticks(ticks=ticks, labels=labels)

            plt.legend(loc='upper left')
            plt.show()

            if self.plot_settings['save_to_file']:
                file_path = self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format('Deaths', self.plotting_settings['country']))

            plt.close(fig)
        else:
            logging.info('Could not find given country "{}"'.format(self.plotting_settings['country']))

        return file_path, plot_name
