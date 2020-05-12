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

class PlotCurveFitSpecificCountry():

    PLOTTING_SETTINGS = {
        # The plot name
        'plot_name': 'Curve fit ({}) for country "{}"',
        'plot_name_prediction': 'Curve fit ({}) for country "{}" with {} day(s) prediction',
        # Plot start day
        'start_day': 84,
        # Plot end day, use a number <= 0 to plot til last day
        'end_day': -1,
        # If prediction for 'predict_days' days should be calculated. 'end_day' will be ignored, deaths not plotted.
        'predict': True,
        # Prediction days
        'predict_days': 4,
        # Boolean flag whether to plot deaths
        'plot_deaths': True,
        # The country to plot
        'country': 'Germany',
        # Plot every n-th tick
        'nth_tick': 2,
        # Plot y-ticks of given steps
        'y_tick_steps': {
            'infections': 20000,
            'deaths': 1000
        },
        # Fitting data for start and end day
        'day_fit': {
            'infections': {
                'start': 97,
                'end': 104,
            },
            'deaths': {
                'start': 97,
                'end': 104,
            }
        },
        # Fitting functions
        'fit_func': {
            'infections': lambda x, a, b: np.exp(a + b * x),
            'deaths': lambda x, a, b: np.exp(a + b * x)
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
        if not self.plotting_settings['predict']:
            plot_name = self.plotting_settings['plot_name'].format('infections', self.plotting_settings['country'])
        else:
            plot_name = self.plotting_settings['plot_name_prediction'].format('infections', self.plotting_settings['country'], self.plotting_settings['predict_days'])

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

            day_end = len(df_melted.Value)
            day_start = 0
            if not self.plotting_settings['raw_data_only']:
                # Validate start and end days
                edf = self.plotting_settings['day_fit']['infections']['end']
                sdf = self.plotting_settings['day_fit']['infections']['start']
                day_end = edf if (edf > 0 and edf < len(df_melted.Value)) else len(df_melted.Value)
                day_start = sdf if sdf > 0 and sdf < day_end else 0
                logging.info('Fitting to days [{}, {}]'.format(day_start, day_end))

            # Validate plot start and end days
            ed = self.plotting_settings['end_day']
            sd = self.plotting_settings['start_day']
            if self.plotting_settings['raw_data_only'] or not self.plotting_settings['predict']:
                plot_day_end = ed if (ed > 0 and ed < len(df_melted.Value)) else len(df_melted.Value)
            else:
                plot_day_end = len(df_melted.Value) + self.plotting_settings['predict_days']
            plot_day_start = sd if sd > 0 and sd < plot_day_end else 0
            logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))

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
                    vals_y_fit = [func(x, params[0], params[1]) for x in vals_x_to_end]
                    ax.plot(vals_x_to_end, vals_y_fit, '--', color ='blue', label ='Fit - days {}-{}'.format(day_start, day_end))

                    # Predict missing n values for prediction
                    if self.plotting_settings['predict']:
                        vx_from = vals_x_to_end[-self.plotting_settings['predict_days']]
                        vals_y_to_end = vals_y_to_end + [func(v, params[0], params[1]) for v in range(vx_from, vx_from + self.plotting_settings['predict_days'])]
                except Exception as e:
                    logging.info('Could not find curve fit: "{}"'.format(e))
            else:
                logging.info('Just logging data')

            # Plot deaths
            if not self.plotting_settings['predict'] and self.plotting_settings['plot_deaths']:
                # Deaths
                df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==self.plotting_settings['country']]
                df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')
                vals_y_deaths_to_end = list(df_deaths_melted.Value)[plot_day_start:plot_day_end]
                ax.plot(vals_x_to_end, vals_y_deaths_to_end, '-', color ='red', label ='Deaths')

            # Plot data
            ax.plot(vals_x_to_end, vals_y_to_end, 'o', color ='green', label ='Infections')
            
            highest_y_value = np.max(vals_y_to_end)

            # Plot prediction background
            if not self.plotting_settings['raw_data_only'] and self.plotting_settings['predict']:
                plt.axvspan(vals_x_to_end[-4] - 0.5, vals_x_to_end[-1] + 0.5, facecolor='b', alpha=0.5, zorder=-100)

            ax.set_title('{} - {} - {}'.format(self.settings['plot']['title'], date_last.date(), plot_name), loc='center')
            ax.set_xlabel(self.settings['plot']['label_x'])
            ax.set_ylabel(self.settings['plot']['label_y'])

            # Calculate ticks and labels (=the dates on the x-axis)
            ticks = [t for t in range(plot_day_start, plot_day_end)][::self.plotting_settings['nth_tick']]
            if self.plotting_settings['plot_days_as_label_x']:
                labels = [d for d in ticks]
            else:
                labels = [str((date_first + datetime.timedelta(days=d)).date()) for d in ticks]
            plt.xticks(ticks=ticks, labels=labels)
            # Calculate y-axis ticks and labels
            to_range = int(highest_y_value / self.plotting_settings['y_tick_steps']['infections']) + 2
            ticks = [t * self.plotting_settings['y_tick_steps']['infections'] for t in range(0, to_range)]
            labels = [d for d in ticks]
            plt.yticks(ticks=ticks, labels=labels)

            plt.legend(loc='upper left')
            plt.show()

            if self.plot_settings['save_to_file']:
                file_path = self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format('Infections', self.plotting_settings['country']))

            plt.close(fig)
        else:
            logging.info('Could not find given country "{}"'.format(self.plotting_settings['country']))

        return file_path, plot_name

    def plot_deaths(self, dates, df_grouped_summed, df_deaths_grouped_summed, date_first, date_last):
        if not self.plotting_settings['predict']:
            plot_name = self.plotting_settings['plot_name'].format('deaths', self.plotting_settings['country'])
        else:
            plot_name = self.plotting_settings['plot_name_prediction'].format('deaths', self.plotting_settings['country'], self.plotting_settings['predict_days'])

        if not self.plot_settings['plot']['deaths']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return None, None

        file_path = ''

        logging.info('Plotting "{}"'.format(plot_name))

        # Gather all countries
        all_countries_list = list(df_grouped_summed['Country/Region'])

        if self.plotting_settings['country'] in all_countries_list:
            fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

            # Infected
            df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==self.plotting_settings['country']]
            df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')

            day_end = len(df_deaths_melted.Value)
            day_start = 0
            if not self.plotting_settings['raw_data_only']:
                # Validate start and end days
                edf = self.plotting_settings['day_fit']['deaths']['end']
                sdf = self.plotting_settings['day_fit']['deaths']['start']
                day_end = edf if (edf > 0 and edf < len(df_deaths_melted.Value)) else len(df_deaths_melted.Value)
                day_start = sdf if sdf > 0 and sdf < day_end else 0
                logging.info('Fitting to days [{}, {}]'.format(day_start, day_end))

            # Validate plot start and end days
            ed = self.plotting_settings['end_day']
            sd = self.plotting_settings['start_day']
            if self.plotting_settings['raw_data_only'] or not self.plotting_settings['predict']:
                plot_day_end = ed if (ed > 0 and ed < len(df_deaths_melted.Value)) else len(df_deaths_melted.Value)
            else:
                plot_day_end = len(df_deaths_melted.Value) + self.plotting_settings['predict_days']
            plot_day_start = sd if sd > 0 and sd < plot_day_end else 0
            logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))

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
                    vals_y_fit = [func(x, params[0], params[1]) for x in vals_x_to_end]
                    ax.plot(vals_x_to_end, vals_y_fit, '--', color ='blue', label ='Fit - days {}-{}'.format(day_start, day_end))

                    # Predict missing n values for prediction
                    if self.plotting_settings['predict']:
                        vx_from = vals_x_to_end[-self.plotting_settings['predict_days']]
                        vals_y_to_end = vals_y_to_end + [func(v, params[0], params[1]) for v in range(vx_from, vx_from + self.plotting_settings['predict_days'])]
                except Exception as e:
                    logging.info('Could not find curve fit: "{}"'.format(e))
            else:
                logging.info('Just logging data')

            # Plot data
            ax.plot(vals_x_to_end, vals_y_to_end, 'o', color ='green', label ='Deaths')
            
            highest_y_value = np.max(vals_y_to_end)

            # Plot prediction background
            if not self.plotting_settings['raw_data_only'] and self.plotting_settings['predict']:
                plt.axvspan(vals_x_to_end[-4] - 0.5, vals_x_to_end[-1] + 0.5, facecolor='b', alpha=0.5, zorder=-100)

            ax.set_title('{} - {} - {}'.format(self.settings['plot']['title'], date_last.date(), plot_name), loc='center')
            ax.set_xlabel(self.settings['plot']['label_x'])
            ax.set_ylabel(self.settings['plot']['label_y'])

            # Calculate ticks and labels (=the dates on the x-axis)
            ticks = [t for t in range(plot_day_start, plot_day_end)][::self.plotting_settings['nth_tick']]
            if self.plotting_settings['plot_days_as_label_x']:
                labels = [d for d in ticks]
            else:
                labels = [str((date_first + datetime.timedelta(days=d)).date()) for d in ticks]
            plt.xticks(ticks=ticks, labels=labels)
            # Calculate y-axis ticks and labels
            to_range = int(highest_y_value / self.plotting_settings['y_tick_steps']['deaths']) + 2
            ticks = [t * self.plotting_settings['y_tick_steps']['deaths'] for t in range(0, to_range)]
            labels = [d for d in ticks]
            plt.yticks(ticks=ticks, labels=labels)

            plt.legend(loc='upper left')
            plt.show()

            if self.plot_settings['save_to_file']:
                file_path = self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format('Deaths', self.plotting_settings['country']))

            plt.close(fig)
        else:
            logging.info('Could not find given country "{}"'.format(self.plotting_settings['country']))

        return file_path, plot_name
