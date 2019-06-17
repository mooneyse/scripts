#!/usr/bin/env python3

'''Calculates the distance between two astronomical sources.'''

import argparse
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord

__author__ = 'Sean Mooney'
__date__ = '22 January 2019'

def distance(ra1, dec1, ra2, dec2):
    '''Calculates the distance between two points on the sky.'''

    s1 = SkyCoord(ra1, dec1, frame='fk5', unit='deg')
    s2 = SkyCoord(ra2, dec2, frame='fk5', unit='deg')

    return s1.separation(s2)


def main():
    '''Evaluates the h5parm phase solutions, makes a new h5parm of the best
    solutions, applies them to the measurement set, and updates the master text
    file with the best solutions after loop 3 is called.'''

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=formatter_class)

    parser.add_argument('-r', '--ra1', required=True, type=str,
                        help='RA of first object (HHhMMmSS.SSs)')
    parser.add_argument('-d', '--dec1', required=True, type=str,
                        help='Declination of first object (+DDdMMmSS.Ss)')
    parser.add_argument('-R', '--ra2', required=True, type=str,
                        help='RA of second object (HHhMMmSS.SSs)')
    parser.add_argument('-D', '--dec2', required=True, type=str,
                        help='Declination of second object (+DDdMMmSS.Ss)')

    args = parser.parse_args()
    ra1 = args.ra1
    ra2 = args.ra2
    dec1 = args.dec1
    dec2 = args.dec2

    separation = distance(ra1, dec1, ra2, dec2)
    d = dict(R1=ra1, D1=dec1, R2=ra2, D2=dec2, S=np.round(separation, 8))
    print('The distance bewteen {R1}, {D1} and {R2}, {D2} is {S}.'.format(**d))


if __name__ == '__main__':
    main()
