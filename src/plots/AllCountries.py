# COVID-19 infections per country
# Copyright 2020 Denis Meyer

# Plot: All countries

import logging
import os
import datetime

import matplotlib.pyplot as plt

class PlotAllCountries():

    PLOTTING_SETTINGS = {
        # The plot name
        'plot_name': 'All countries',
        # Plot start day
        'start_day': -1,
        # Plot end day, use a number <= 0 to plot til last day
        'end_day': -1,
        # Plot every n-th tick
        'nth_tick': 5,
        # Boolean flag whether to plot days as x-label instead of dates
        'plot_days_as_label_x': False
    }

    def __init__(self, functions, settings, plot_settings, plotting_settings=PLOTTING_SETTINGS):
        self.functions = functions
        self.settings = settings
        self.plot_settings = plot_settings
        self.plotting_settings = plotting_settings

    def plot(self, dates, df_grouped_summed, date_first, date_last):
        plot_name = self.plotting_settings['plot_name']

        if not self.plot_settings['plot']:
            logging.info('Skipping plot "{}"'.format(plot_name))
            return None, None

        logging.info('Plotting "{}"'.format(plot_name))

        countries = df_grouped_summed['Country/Region']

        # Plot
        fig, ax = plt.subplots(figsize=self.settings['plot']['size'])

        # Validate plot start and end days
        ed = self.plotting_settings['end_day']
        plot_day_end = ed if (ed > 0 and ed < len(dates)) else len(dates)
        sd = self.plotting_settings['start_day']
        plot_day_start = sd if sd > 0 and sd < plot_day_end else 0
        logging.info('Plotting to days [{}, {}]'.format(plot_day_start, plot_day_end))

        for i, cr in enumerate(countries):
            # Infected
            df_tmp = df_grouped_summed[df_grouped_summed['Country/Region']==cr]
            df_melted = df_tmp.melt(id_vars=df_tmp.columns.values[:1], var_name='Date', value_name='Value')[plot_day_start:plot_day_end]
            vals_x_to_end = [t for t in range(plot_day_start, plot_day_end)]
            ax.plot(vals_x_to_end, df_melted['Value'], '-', label='{}'.format(cr))

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
            file_path = self.functions.save_plot(os.getcwd(), fig, self.settings['plot_image_path'], date_last, self.plot_settings['filename'])

        plt.close(fig)

        return file_path, plot_name
