#!/usr/bin/env python2.7

'''Plot HDF5 solutions for a specified station from two HDF5 files.'''

from __future__ import print_function
import argparse
import numpy as np
import sys
import losoto.h5parm as lh5
from losoto.lib_operations import reorderAxes
import matplotlib.pyplot as plt

__author__ = 'Sean Mooney'
__date__ = '01 June 2019'

def get_values(h5, station='ST001', polarisation='XX'):
    station_exists=False
    h = lh5.h5parm(h5, readonly=True)
    phase = h.getSolset('sol000').getSoltab('phase000')
    time = phase.time
    for ant in range(len(phase.ant)):
        if phase.ant[ant] == station:
            station_exists = True
            break

    if not station_exists:
        print('{} does not exist in {}.'.format(station, h5))
        h.close()
        sys.exit()

    try:
        reordered_values = reorderAxes(phase.val, phase.getAxesNames(), ['time', 'freq', 'ant', 'pol', 'dir'])
        my_values_xx = reordered_values[:, 0, ant, 0, 0]
        my_values_yy = reordered_values[:, 0, ant, 1, 0]
    except:
        reordered_values = reorderAxes(phase.val, phase.getAxesNames(), ['time', 'freq', 'ant', 'pol'])
        my_values_xx = reordered_values[:, 0, ant, 0]
        my_values_yy = reordered_values[:, 0, ant, 1]

    h.close()
    if polarisation == 'XX':
        values = my_values_xx
    elif polarisation == 'YY':
        values = my_values_yy

    return values, time


def plot_values(values1, times1, values2, times2, values3, times3, station='ST001', polarisation='XX'):
    plt.title('{}, {} (coherence: {:.3f})'.format(station, polarisation, coherence_metric(values1, values2)))
    plt.plot(times1, values1, 'r-', label='Original 1', lw=1)
    plt.plot(times2, values2, 'g-', label='Original 2', lw=2)
    plt.plot(times3, values3, 'b-', label='New', lw=3)
    plt.xlim(min([min(times1), min(times2)]), max([max(times1), max(times2)]))
    plt.ylim(-np.pi, np.pi)
    plt.xlabel('Time')
    plt.ylabel('Phase')
    plt.legend()
    plt.tight_layout()
    plt.show()


def interpolate_nan(x_):
    x_ = np.array(x_)
    nans, x = np.isnan(x_), lambda z: z.nonzero()[0]
    x_[nans] = np.interp(x(nans), x(~nans), x_[~nans])
    return x_


def coherence_metric(xx, yy):
    xx, yy = interpolate_nan(xx), interpolate_nan(yy)
    return np.nanmean(np.gradient(abs(np.unwrap(xx - yy))) ** 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('h5a', type=str)
    parser.add_argument('h5b', type=str)
    parser.add_argument('h5c', type=str)
    parser.add_argument('-s', '--station', required=False, type=str, default='ST001')
    parser.add_argument('-p', '--polarisation', required=False, type=str, default='XX')

    args = parser.parse_args()
    h5a = args.h5a
    h5b = args.h5b
    h5c = args.h5c
    station = args.station
    polarisation = args.polarisation

    values1, times1 = get_values(h5a, station=station, polarisation=polarisation)
    values2, times2 = get_values(h5b, station=station, polarisation=polarisation)
    values3, times3 = get_values(h5c, station=station, polarisation=polarisation)

    plot_values(values1, times1, values2, times2, values3, times3, station=station, polarisation=polarisation)


if __name__ == '__main__':
    main()
