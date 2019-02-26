#!/usr/bin/env python3

'''Plot the spectral energy distribution for a source from a downloaded table
from NED.'''

import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from astropy import coordinates
from astropy import units as u
from PIL import Image, ImageDraw
from astroquery.ned import Ned as ned

__author__ = 'Sean Mooney'
__email__ = 'sean.mooney@ucdconnect.ie'
__date__ = '08 February 2019'

def TeV_to_MHz(TeV=50):
    '''Use astropy to find the equivalency between MHz and TeV, which I used to
    find the ideal frequency axis range for the blazar SEDs.'''

    exact = (TeV * u.TeV).to(u.MHz, equivalencies=u.spectral()).value
    return 10 ** np.round(np.log10(exact))  # nearest power of 10


def do_plotting(name, frequency, nu_f_nu, savefig, fontsize=16, dpi=96, l=529,
    w=387):
    '''Use Matplotlib to build the plot. DPI found from
    https://www.infobyip.com/detectmonitordpi.php.'''

    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'
    mpl.rcParams['xtick.top'] = True
    mpl.rcParams['ytick.right'] = True
    mpl.rcParams['xtick.major.size'] = 10
    mpl.rcParams['xtick.major.width'] = 2
    mpl.rcParams['xtick.minor.size'] = 5
    mpl.rcParams['xtick.minor.width'] = 2
    mpl.rcParams['ytick.major.size'] = 10
    mpl.rcParams['ytick.major.width'] = 2
    mpl.rcParams['ytick.minor.size'] = 5
    mpl.rcParams['ytick.minor.width'] = 2
    mpl.rcParams['axes.linewidth'] = 2

    # plt.figure(figsize=(12, 8))
    plt.figure(figsize=(l / dpi, w / dpi), dpi=dpi)
    plt.loglog(frequency, nu_f_nu, marker='.', ls='None', color='black')
    plt.plot(frequency[-2], nu_f_nu[-2], marker='.', ls='None', color='red')
    plt.xlim(1e7, 1e26)
    plt.ylim(1e7, 1e14)
    plt.xlabel(r'$\nu$ (Hz)', fontsize=fontsize)
    plt.ylabel(r'$\nu \cdot f_{\nu}$ (Jy Hz)', fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.minorticks_off()
    plt.tight_layout()
    plt.savefig(savefig, dpi=dpi)
    plt.close()  # close open figures


def make_sed(ned_name='OJ 287', savefig='/home/sean/Downloads/images/oj287-sed.png'):
    '''Plot the SED from NED data.'''

    photometry = ned.get_table(ned_name, table='photometry')
    frequency = photometry['Frequency']  # hertz
    flux = photometry['Flux Density']  # jansky
    nu_f_nu = np.array(frequency) * np.array(flux)
    do_plotting(ned_name, frequency, nu_f_nu, savefig)


def main():
    '''Query NED for the spectral information for a source, given the name.'''

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter_class)

    make_sed()


if __name__ == '__main__':
    main()
