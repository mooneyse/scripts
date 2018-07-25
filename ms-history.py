#!/usr/bin/env python3

'''
    Credit: LOFAR-Contributions/Maintained/msHistory.py
    Usage:  ./ms-history.py -i ms.ms -v
    Detail: Prints out the history of a LOFAR measurement set. Can be used to
            see if a source had been demixed by the observatory, for example.
    Edits:  Updated for Python 3.
'''

import pyrap.tables as pt
import optparse

def main(ms = '', verbose = False):
        didWarn = False
        whatSkipped = {}
        t = pt.table(ms, ack = False)
        th = pt.table(t.getkeyword('HISTORY'), ack = False)
        colnames = th.colnames()
        nrows = th.nrows()
        print('The HISTORY table in %s has %d rows' % (ms, nrows))
        for row in th:
                if row['APPLICATION'] == 'imager' or row['APPLICATION'] == 'OLAP' or row['APPLICATION'] == 'ms':
                        if verbose:
                                print('%s was run at time %f with parameters:' % (row['APPLICATION'], row['TIME']))
                                for r in row['APP_PARAMS']:
                                        print('\t%s' % (r))
                        else:
                                if not didWarn:
                                        print('(Skipping OLAP, imager, and ms rows, use -v to print them)')
                                        didWarn = True
                                if row['APPLICATION'] in whatSkipped:
                                        whatSkipped[row['APPLICATION']] += 1
                                else:
                                        whatSkipped[row['APPLICATION']] = 1
                else:
                        print('%s was run at time %f with parameters:' % (row['APPLICATION'], row['TIME']))
                        for r in row['APP_PARAMS']:
                                print('\t%s' % (r))
        print('Overview of skipped rows:')
        for key in whatSkipped:
                print('\t%s:\tskipped %d times' % (key,whatSkipped[key]))

opt = optparse.OptionParser()
opt.add_option('-i', '--ms', help = 'Input MS [no default]', default = '')
opt.add_option('-v', '--verbose', help = 'Verbose [default False]', default = False, action = 'store_true')
options, args = opt.parse_args()
main(ms = options.ms, verbose = options.verbose)
