#!/usr/bin/env python3

'''Plot a FITS file.'''

import aplpy
import argparse
import os
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt

__author__ = 'Sean Mooney'
__date__ = '22 January 2019'

# TODO have a flag to set the format (png or eps)
# TODO have a flag to plt.show() or not
# TODO add show_markers functionality
# TODO add a greyscale or colour flag

def plot_fits(fits, color=True, cmap='viridis', vmin=0, vmax=12, format='png'):
    '''Plot a FITS file.'''

    plt.rcParams['font.family'] = 'serif'
    image = aplpy.FITSFigure(fits)

    if color:
        image.show_colorscale(cmap=cmap, vmin=vmin, vmax=vmax)
    else:
        image.show_grayscale()

    image.show_contour(fits, levels=[4, 8], colors='white')
    image.recenter(194.2401688, 47.33874257, radius=0.00416667)
    # ra = [187.2740917, 187.2779167]
    # dec = [2.0485000, 2.0525000]
    # image.show_markers(ra, dec, edgecolor='None', facecolor='#16A085',
    #                    marker='+', s=500, alpha=0.8, linewidth=2)
    image.tick_labels.set_font(size=15)
    image.axis_labels.set_font(size=15)
    # plt.show()
    image.save(os.path.splitext(fits)[0] + '.' + format, format=format)

    return os.path.splitext(fits)[0] + '.' + format


def main():
    '''Plot a FITS file.'''

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter_class)

    parser.add_argument('-f',
                        '--fits',
                        required=True,
                        type=str,
                        help='FITS file to be plotted.')

    args = parser.parse_args()
    fits = args.fits

    plot = plot_fits(fits)
    print('All done! The image is at {}.'.format(plot))

if __name__ == '__main__':
    main()
