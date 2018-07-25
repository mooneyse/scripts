#!/usr/bin/env python2.7
 
'''
    Credit: Sean Mooney
    Usage:  ./amplitude-versus-time.py -i ms.ms -a 100 -n all
    Detail: argv[1] is the MS and argv[2] is the averaging factor. If
            argv[3] == all then a plot is made for each channel. Otherwise, only
            the first channel is plotted.
    To do:  Edit so it will only import every Nth point and be faster.
'''

import argparse, os, sys
import numpy as np
import pyrap.tables as pt
import matplotlib.pyplot as plt

def main(ms, average, channels):
    t = pt.table(ms, ack = False)
    data = t.getcol('DATA', startrow = 0, nrow = -1, rowincr = average)

    print 'Polarisations:', np.size(data[0, 0, :])
    print 'Channels:     ', np.size(data[0, :, 0])

    if channels:
        the_range = range(0, np.size(data[0, :, 0]))
    else:
        the_range = range(1)

    for channel in the_range:
        print 'Working on channel ' + str(channel) + '...'
        xx, yy = [], []
        for i in range(np.size(data[:, 0, 0])):
            xx.append(abs(data[i, channel, 0]))
            yy.append(abs(data[i, channel, 3]))

        plt.figure(figsize = (13.92, 8.60))
        plt.plot(xx, ls = 'None', marker = '.', color = 'red', label = 'XX')
        plt.plot(yy, ls = 'None', marker = '.', color = 'blue', label = 'YY')
        plt.title(ms + ' channel ' + str(channel))
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.xlim(0, len(xx))
        plt.legend(numpoints = 1)
        plt.savefig(os.path.splitext(ms)[0] + '-ch' + str(channel) + '.png')

    print 'All done!'
    t.close()

parser = argparse.ArgumentParser(description = 'Plot the amplitude versus time for a LOFAR measurement set.')
parser.add_argument('-m', '--ms', help = 'Input MS', dest = 'ms', required = True)
parser.add_argument('-a', '--average', help = 'Sampling frequency', dest = 'average', default = 1, type = int)
parser.add_argument('-c', '--channels', help = 'Plot all channels', dest = 'channels', default = False, action = 'store_true')
args = parser.parse_args()

if __name__ == "__main__":
    main(args.ms, args.average, args.channels)
