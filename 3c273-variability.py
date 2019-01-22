#!/usr/bin/env python3

'''Plotting the variability of the core of 3C 273 using data at 37 GHz taken
from http://isdc.unige.ch/3c273/.'''

import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

__author__ = 'Sean Mooney'
__email__ = 'sean.mooney@ucdconnect.ie'
__date__ = '03 January 2019'

def set_style():
    '''This sets reasonable defaults for font size for a figure that will go in
       a paper.'''

    plt.style.use(['seaborn-white', 'seaborn-paper'])
    matplotlib.rc('font', family='Times New Roman')
    matplotlib.rcParams['mathtext.fontset'] = 'custom'
    matplotlib.rcParams['mathtext.rm'] = 'serif'
    matplotlib.rcParams['mathtext.it'] = 'serif:italic'
    matplotlib.rcParams['mathtext.default'] = 'it'

def main():
    '''Do the analysis.'''

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter_class)

    parser.add_argument('-c',
                        '--csv',
                        required=False,
                        type=str,
                        default='/home/sean/Downloads/workbooks/3c273.csv',
                        help='CSV containing 3C 273 variability data')

    args = parser.parse_args()
    csv = args.csv

    # seaborn and pandas options
    set_style()
    pd.set_option('expand_frame_repr', False)
    pd.set_option('display.max_columns', None)

    # manually removed whitespace from the header
    usecols = ['Date_[Year]', 'Frequency_[Hz]', 'Flux_[Jy]', 'FluxError_[Jy]', 'Flag']
    df = pd.read_csv(csv, delim_whitespace=True, skiprows=[0, 1, 3], usecols=usecols)
    df.columns = ['date', 'frequency', 'flux', 'error', 'flag']  # rename columns

    old_rows = df.shape[0]
    df = df[df.flag != -1]  # remove flagged rows
    print(old_rows - df.shape[0], 'flagged rows removed.')

    df = df[df.date > 1990]  # remove data before 1990

    print('Frequency information:')
    print('Minimum:', df['frequency'].min() / 1e9, 'GHz')
    print('Maximum:', df['frequency'].max() / 1e9, 'GHz')
    print('Mean:', round(df['frequency'].mean() / 1e9, 0), 'GHz')
    print('Median:', df['frequency'].median() / 1e9, 'GHz')
    print('Mode:', df['frequency'].mode()[0] / 1e9, 'GHz')

    print('Flux density information:')
    print('Minimum:', df['flux'].min(), 'Jy')
    print('Maximum:', df['flux'].max(), 'Jy')

    # do the plotting
    plt.figure(figsize=(16, 8))

    size = 32
    plt.rc('font', size=size)  # controls default text sizes
    plt.rc('axes', titlesize=size)  # fontsize of the axes title
    plt.rc('axes', labelsize=size)  # fontsize of the x and y labels
    plt.rc('xtick', labelsize=size)  # fontsize of the tick labels
    plt.rc('ytick', labelsize=size)  # fontsize of the tick labels

    plt.xlabel('Time')
    plt.ylabel(r'$S_\nu$ (Jy)')
    plt.errorbar(df['date'], df['flux'], yerr=df['error'], fmt='none', ecolor='black')
    plt.xlim([1990, 2005])

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
