# COVID-19 infections per country
# Copyright 2020 Denis Meyer

# Plot: Curve fit multiple countries

import logging
import os
import datetime

import matplotlib.pyplot as plt
from heapq import nlargest
import scipy.optimize
import numpy as np

class PlotCurveFitMultiCountries():

    PLOTTING_SETTINGS = {
        # The plot name
        'plot_name': 'Curve fit ({}) for countries "{}"',
        'plot_name_prediction': 'Curve fit ({}) for countries "{}" with {} days prediction',
        # Plot start day
        'start_day': 75,
        # Plot end day, use a number <= 0 to plot til last day
        'end_day': -1,
        # Boolean flag whether to plot deaths
        'plot_deaths': True,
        # If prediction for 'predict_days' days should be calculated. 'end_day' will be ignored, deaths not plotted.
        'predict': True,
        # Prediction days
        'predict_days': 4,
        # Plot every n-th tick
        'nth_tick': 3,
        # Plot y-ticks of given steps
        'y_tick_steps': {
            'infections': 50000,
            'deaths': 5000
        },
        # Country and fitting data
        'countries': [
            {
                'name': 'Italy',
                'day_fit': {
                    'infections': {
                        'start': 92,
                        'end': 99,
                    },
                    'deaths': {
                        'start': 92,
                        'end': 99,
                    }
                },
                'color': 'tomato'
            },
            {
                'name': 'US',
                'day_fit': {
                    'infections': {
                        'start': 91,
                        'end': 98,
                    },
                    'deaths': {
                        'start': 91,
                        'end': 98,
                    }
                },
                'color': 'seagreen'
            },
            {
                'name': 'Spain',
                'day_fit': {
                    'infections': {
                        'start': 92,
                        'end': 99,
                    },
                    'deaths': {
                        'start': 92,
                        'end': 99,
                    }
                },
                'color': 'gold'
            },
            {
                'name': 'Germany',
                'day_fit': {
                    'infections': {
                        'start': 92,
                        'end': 99,
                    },
                    'deaths': {
                        'start': 92,
                        'end': 99,
                    }
                },
                'color': 'lightskyblue'
            }
        ],
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
        countries = [x['name'] for x in self.plotting_settings['countries']]
        if not self.plotting_settings['predict']:
            plot_name = self.plotting_settings['plot_name'].format('infections', ', '.join(countries))
        else:
            plot_name = self.plotting_settings['plot_name_prediction'].format('infections', ', '.join(countries), self.plotting_settings['predict_days'])

        if not self.plot_settings['plot']['infections']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return None, None

        logging.info('Plotting "{}"'.format(plot_name))

        # Gather all countries
        all_countries_list = list(df_grouped_summed['Country/Region'])

        fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

        # Validate plot start and end days
        ed = self.plotting_settings['end_day']
        sd = self.plotting_settings['start_day']
        if self.plotting_settings['raw_data_only'] or not self.plotting_settings['predict']:
            plot_day_end = ed if (ed > 0 and ed < len(dates)) else len(dates)
        else:
            plot_day_end =len(dates) + self.plotting_settings['predict_days']
        plot_day_start = sd if sd > 0 and sd < plot_day_end else 0

        logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))

        lowest_start_day = len(dates)
        highest_end_day = 0
        highest_y_value = -1
        for country in self.plotting_settings['countries']:
            logging.info('Preparing country "{}"'.format(country['name']))
            country_name = country['name']

            if country_name in all_countries_list:
                # Infected
                df_tmp = df_grouped_summed[df_grouped_summed['Country/Region']==country_name]
                df_melted = df_tmp.melt(id_vars=df_tmp.columns.values[:1], var_name='Date', value_name='Value')

                # Check best fit data for start and end day
                start_day = country['day_fit']['infections']['start']
                end_day = country['day_fit']['infections']['end']
                day_end = len(dates)
                day_start = 0
                if not self.plotting_settings['raw_data_only']:
                    # Validate start and end days
                    day_end = end_day if (end_day > 0 and end_day < len(dates)) else len(dates)
                    day_start = start_day if start_day > 0 and start_day < day_end else 0
                    logging.info('Fitting to days [{}, {}]'.format(day_start, day_end))
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
                        ax.plot(vals_x_to_end, vals_y_fit, '-', color=country['color'], label='{} (Fit - days {}-{})'.format(country_name, day_start, day_end))

                        # Predict missing n values for prediction
                        if not self.plotting_settings['raw_data_only'] and self.plotting_settings['predict']:
                            vx_from = vals_x_to_end[-self.plotting_settings['predict_days']]
                            vals_y_to_end = vals_y_to_end + [self.functions.fit(v, params[0], params[1]) for v in range(vx_from, vx_from + self.plotting_settings['predict_days'])]
                    except Exception as e:
                        logging.info('Could not find curve fit: {}'.format(e))
                else:
                    logging.info('Just logging data')

                # Plot data
                ax.plot(vals_x_to_end, vals_y_to_end, 'o', color=country['color'], label='{} (Infections)'.format(country_name))

                y_max = np.max(vals_y_to_end)
                if y_max > highest_y_value:
                    highest_y_value = y_max

                # Plot deaths
                if not self.plotting_settings['predict'] and self.plotting_settings['plot_deaths']:
                    # Deaths
                    df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==country_name]
                    df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')

                    vals_x_to_end = [t for t in range(lowest_start_day, highest_end_day)]
                    vals_y_deaths_to_end = list(df_deaths_melted.Value)[lowest_start_day:highest_end_day]
                    ax.plot(vals_x_to_end, vals_y_deaths_to_end, '--', color=country['color'], label='{} (Deaths)'.format(country_name))
            else:
                logging.info('Could not find given country "{}"'.format(country_name))

        ax.set_title('{} - {} - {}'.format(self.settings['plot']['title'], date_last.date(), plot_name), loc='center')
        ax.set_xlabel(self.settings['plot']['label_x'])
        ax.set_ylabel(self.settings['plot']['label_y'])

        # Plot prediction background
        if not self.plotting_settings['raw_data_only'] and self.plotting_settings['predict']:
            plt.axvspan(vals_x_to_end[-4] - 0.5, vals_x_to_end[-1] + 0.5, facecolor='b', alpha=0.5, zorder=-100)

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

        file_path = ''
        if self.plot_settings['save_to_file']:
            file_path = self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format('Infections', '-'.join(countries)))

        plt.close(fig)

        return file_path, plot_name

    def plot_deaths(self, dates, df_grouped_summed, df_deaths_grouped_summed, date_first, date_last):
        countries = [x['name'] for x in self.plotting_settings['countries']]
        if not self.plotting_settings['predict']:
            plot_name = self.plotting_settings['plot_name'].format('deaths', ', '.join(countries))
        else:
            plot_name = self.plotting_settings['plot_name_prediction'].format('deaths', ', '.join(countries), self.plotting_settings['predict_days'])

        if not self.plot_settings['plot']['deaths']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return None, None

        logging.info('Plotting "{}"'.format(plot_name))

        # Gather all countries
        all_countries_list = list(df_grouped_summed['Country/Region'])

        fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

        # Validate plot start and end days
        ed = self.plotting_settings['end_day']
        sd = self.plotting_settings['start_day']
        if self.plotting_settings['raw_data_only'] or not self.plotting_settings['predict']:
            plot_day_end = ed if (ed > 0 and ed < len(dates)) else len(dates)
        else:
            plot_day_end =len(dates) + self.plotting_settings['predict_days']
        plot_day_start = sd if sd > 0 and sd < plot_day_end else 0
        logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))

        lowest_start_day = len(dates)
        highest_end_day = 0
        highest_y_value = -1
        for country in self.plotting_settings['countries']:
            logging.info('Preparing country "{}"'.format(country['name']))
            country_name = country['name']

            if country_name in all_countries_list:
                # Infected
                df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==country_name]
                df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')

                # Check best fit data for start and end day
                start_day = country['day_fit']['deaths']['start']
                end_day = country['day_fit']['deaths']['end']
                day_end = len(dates)
                day_start = 0
                if not self.plotting_settings['raw_data_only']:
                    # Validate start and end days
                    day_end = end_day if (end_day > 0 and end_day < len(dates)) else len(dates)
                    day_start = start_day if start_day > 0 and start_day < day_end else 0
                    logging.info('Fitting to days [{}, {}]'.format(day_start, day_end))
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
                        ax.plot(vals_x_to_end, vals_y_fit, '-', color=country['color'], label='{} (Fit - days {}-{})'.format(country_name, day_start, day_end))

                        # Predict missing n values for prediction
                        if self.plotting_settings['predict']:
                            vx_from = vals_x_to_end[-self.plotting_settings['predict_days']]
                            vals_y_to_end = vals_y_to_end + [self.functions.fit(v, params[0], params[1]) for v in range(vx_from, vx_from + self.plotting_settings['predict_days'])]
                    except Exception as e:
                        logging.info('Could not find curve fit, exception: {}'.format(e))
                else:
                    logging.info('Just logging data')

                # Plot data
                ax.plot(vals_x_to_end, vals_y_to_end, 'o', color=country['color'], label='{}'.format(country_name))

                y_max = np.max(vals_y_to_end)
                if y_max > highest_y_value:
                    highest_y_value = y_max
            else:
                logging.info('Could not find given country "{}"'.format(country_name))

        ax.set_title('{} - {} - {}'.format(self.settings['plot']['title'], date_last.date(), plot_name), loc='center')
        ax.set_xlabel(self.settings['plot']['label_x'])
        ax.set_ylabel(self.settings['plot']['label_y'])

        # Plot prediction background
        if not self.plotting_settings['raw_data_only'] and self.plotting_settings['predict']:
            plt.axvspan(vals_x_to_end[-4] - 0.5, vals_x_to_end[-1] + 0.5, facecolor='b', alpha=0.5, zorder=-100)

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

        file_path = ''
        if self.plot_settings['save_to_file']:
            file_path = self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format('Deaths', '-'.join(countries)))

        plt.close(fig)

        return file_path, plot_name
