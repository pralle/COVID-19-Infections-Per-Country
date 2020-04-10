# COVID-19 infections per country
# Copyright 2020 Denis Meyer

# Plot: Countries with highest numbers

import logging
import os
import datetime

import matplotlib.pyplot as plt
from heapq import nlargest

class PlotHighestCountries():

    PLOTTING_SETTINGS = {
        # The plot name
        'plot_name': '{} countries with highest number of {}',
        # Plot start day
        'start_day': 46,
        # Plot end day, use a number <= 0 to plot til last day
        'end_day': -1,
        # Plot every n-th tick
        'nth_tick': 3,
        # Boolean flag whether to plot deaths
        'plot_deaths': True,
        # Number of countries to plot
        'nr_countries': 10,
        # Boolean flag whether to plot days as x-label instead of dates
        'plot_days_as_label_x': False
    }

    def __init__(self, functions, settings, plot_settings, plotting_settings=PLOTTING_SETTINGS):
        self.functions = functions
        self.settings = settings
        self.plot_settings = plot_settings
        self.plotting_settings = plotting_settings

    def plot_infections(self, dates, df_grouped_summed, df_deaths_grouped_summed, date_first, date_last):
        plot_name = self.plotting_settings['plot_name'].format(self.plotting_settings['nr_countries'], 'infections')

        if not self.plot_settings['plot']['infections']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return

        logging.info('Plotting "{}"'.format(plot_name))

        # Validate plot start and end days
        ed = self.plotting_settings['end_day']
        sd = self.plotting_settings['start_day']
        plot_day_end = ed if (ed > 0 and ed < len(dates)) else len(dates)
        plot_day_start = sd if sd > 0 and sd < plot_day_end else 0
        logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))

        # Calculate the n highest countries
        dict_highest_all = {}
        countries = df_grouped_summed['Country/Region']
        for cr in countries:
            # Infected
            df_tmp = df_grouped_summed[df_grouped_summed['Country/Region']==cr]
            df_melted = df_tmp.melt(id_vars=df_tmp.columns.values[:1], var_name='Date', value_name='Value')
            dict_highest_all[cr] = df_melted.max().Value

        # Extract the n highest country names
        countries = nlargest(self.plotting_settings['nr_countries'], dict_highest_all, key=dict_highest_all.get)

        # Plot
        fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

        # Calculate color map
        cmap = self.functions.get_cmap(self.plotting_settings['nr_countries'])

        for i, cr in enumerate(countries):
            # Infected
            df_tmp = df_grouped_summed[df_grouped_summed['Country/Region']==cr]
            df_melted = df_tmp.melt(id_vars=df_tmp.columns.values[:1], var_name='Date', value_name='Value')[plot_day_start:plot_day_end]
            vals_x_to_end = [t for t in range(plot_day_start, plot_day_end)]
            ax.plot(vals_x_to_end, df_melted['Value'], '-', color=cmap(i), label='{} (Infections)'.format(cr))

            # Deaths
            if self.plotting_settings['plot_deaths']:
                df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==cr]
                df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')[plot_day_start:plot_day_end]
                ax.plot(vals_x_to_end, df_deaths_melted['Value'], '--', color=cmap(i), label='{} (Deaths)'.format(cr))

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

        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        plt.show()

        if self.plot_settings['save_to_file']:
            self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format(self.plotting_settings['nr_countries'], 'Infections'))

        plt.close(fig)

    def plot_deaths(self, dates, df_grouped_summed, df_deaths_grouped_summed, date_first, date_last):
        plot_name = self.plotting_settings['plot_name'].format(self.plotting_settings['nr_countries'], 'deaths')

        if not self.plot_settings['plot']['deaths']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return

        logging.info('Plotting "{}"'.format(plot_name))

        # Validate plot start and end days
        ed = self.plotting_settings['end_day']
        sd = self.plotting_settings['start_day']
        plot_day_end = ed if (ed > 0 and ed < len(dates)) else len(dates)
        plot_day_start = sd if sd > 0 and sd < plot_day_end else 0
        logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))

        # Calculate the n highest countries
        dict_highest_all = {}
        countries = df_deaths_grouped_summed['Country/Region']
        for cr in countries:
            # Deaths
            df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==cr]
            df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')
            dict_highest_all[cr] = df_deaths_melted.max().Value

        # Extract the n highest country names
        countries = nlargest(self.plotting_settings['nr_countries'], dict_highest_all, key=dict_highest_all.get)

        # Plot
        fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

        for cr in countries:
            # Deaths
            df_deaths_tmp = df_deaths_grouped_summed[df_deaths_grouped_summed['Country/Region']==cr]
            df_deaths_melted = df_deaths_tmp.melt(id_vars=df_deaths_tmp.columns.values[:1], var_name='Date', value_name='Value')[plot_day_start:plot_day_end]
            vals_x_to_end = [t for t in range(plot_day_start, plot_day_end)]
            ax.plot(vals_x_to_end, df_deaths_melted['Value'], '-', label=cr)

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

        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        plt.show()

        if self.plot_settings['save_to_file']:
            self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'].format(self.plotting_settings['nr_countries'], 'Deaths'))

        plt.close(fig)
