#!/usr/bin/env python2

''' I did a diagonal solve on 3C 273 to see how the calibration went. Now, I
want to make a plot of the dynamic spectrum per station for both phase and
amplitude to look for RFI. '''

from __future__ import print_function
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import losoto.h5parm as h5
import sys

__author__ = 'Sean Mooney'
__email__ = 'sean.mooney@ucdconnect.ie'
__date__ = '20 June 2019'

def plot(solns, values, ant, idx, polname):
        pol = 0 if polname is 'XX' else 1
        thresh = 5 * np.nanmedian(values[:, :, idx, pol])
        masked = ma.masked_greater(values[:, :, idx, pol], thresh) if solns == 'amplitude' else values[:, :, idx, pol]

        mskd, _ = np.argwhere(values[:, :, idx, pol] > thresh).shape
        plt.figure(figsize=(16, 9))
        plt.imshow(np.transpose(masked), aspect='auto', cmap='spring')
        title = ant +  ' ' + solns + ' ' + polname + ' (>' + str(np.round(thresh, 2)) + ', ' + str(mskd)  + ' masked)' if solns == 'amplitude' else ant +  ' ' + solns + ' ' + polname
        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.colorbar()
#        plt.show()
        plt.savefig('/data5/sean/hba/3c273-tests/' + solns  + '-' + ant +'-' + polname  + '.png')
        print(solns  + ' ' + ant +' ' + polname  + ' ' + str(np.round(thresh, 5)))


def main():
    my_h5 = '/data5/sean/hba/3c273-tests/concatenate.gaincal.solutions.h5'
    my_solset = 'sol000'
    my_solutions = ['amplitude']  # , 'phase']
    my_polarisations = ['XX', 'YY']

    h = h5.h5parm(my_h5)
    solset = h.getSolset(my_solset)

    for solutions in my_solutions:
        my_soltab = solutions + '000'
        soltab = solset.getSoltab(my_soltab)

        for	i, ant in enumerate(soltab.ant):
            for polname in my_polarisations:
                plot(solns=solutions, values=soltab.val, ant=ant, idx=i, polname=polname)
#                sys.exit()
    h.close()


if __name__ == '__main__':
    main()
