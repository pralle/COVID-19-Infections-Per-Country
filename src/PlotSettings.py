# COVID-19 infections per country
# Copyright 2020 Denis Meyer

# Plot settings

# Ignores all plotting flags and plots (except "all countries")
FORCE_PLOT = True
# Ignores all flags "..._SAVE_PLOT_TO_FILE" and saves to file - plotting must be activated
FORCE_SAVE_PLOT_TO_FILE = False

PLOT_SETTINGS = {
    # Plot: All countries
    'all_countries': {
        # Boolean flag whether to plot
        'plot': False,
        # Boolean flag whether to save the plot to file
        'save_to_file': FORCE_SAVE_PLOT_TO_FILE or False,
        # The file name
        'filename': 'All-Countries.png',
    },
    # Plot: Specific countries
    'specific_countries': {
        # Boolean flags whether to plot
        'plot': {
            'infections': FORCE_PLOT or False,
            'deaths': FORCE_PLOT or False
        },
        # Boolean flag whether to save the plot to file
        'save_to_file': FORCE_SAVE_PLOT_TO_FILE or False,
        # The file name
        'filename': 'Specific-Countries-{}-{}.png',
    },
    # Plot: Countries with highest numbers
    'highest_countries': {
        # Boolean flags whether to plot
        'plot': {
            'infections': FORCE_PLOT or False,
            'deaths': FORCE_PLOT or False
        },
        # Boolean flag whether to save the plot to file
        'save_to_file': FORCE_SAVE_PLOT_TO_FILE or False,
        # The file name
        'filename': '{}-Countries-With-Highest-Number-Of-{}.png',
    },
    # Plot: Curve fit specific country
    'curve_fit_specific_country': {
        # Boolean flags whether to plot
        'plot': {
            'infections': FORCE_PLOT or False,
            'deaths': FORCE_PLOT or False
        },
        # Boolean flag whether to save the plot to file
        'save_to_file': FORCE_SAVE_PLOT_TO_FILE or False,
        # The file name
        'filename': 'Curve-Fit-{}-{}.png',
    },
    # Plot: Curve fit specific country
    'multi_curve_fit_specific_country': {
        # Boolean flags whether to plot
        'plot': {
            'infections': FORCE_PLOT or False,
            'deaths': FORCE_PLOT or False
        },
        # Boolean flag whether to save the plot to file
        'save_to_file': FORCE_SAVE_PLOT_TO_FILE or False,
        # The file name
        'filename': 'Multi-Curve-Fit-{}-{}.png',
    },
    # Plot: Curve fit multiple countries
    'curve_fit_multi_countries': {
        # Boolean flags whether to plot
        'plot': {
            'infections': FORCE_PLOT or False,
            'deaths': FORCE_PLOT or False
        },
        # Boolean flag whether to save the plot to file
        'save_to_file': FORCE_SAVE_PLOT_TO_FILE or False,
        # The file name
        'filename': 'Curve-Fit-{}-{}.png',
    }
}
