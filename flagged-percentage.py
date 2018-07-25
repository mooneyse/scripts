#!/usr/bin/env python3

'''
    Credit: Sean Mooney
    Usage:  ./flagged-percentage.py ms.ms
    Detail: Check what fraction of the data have been flagged.
'''

import glob, os, sys

# define function to save to file
def save_to_file(my_ms, my_string, my_file):
    with open(my_file, 'a') as the_file:
        the_file.write(my_ms + ' ' + my_string)

# define stuff
text_file = sys.argv[0][:-3] + '.log'
output = sys.argv[0][:-3] + '.txt'
the_string = 'Total flagged:'
ms_list = glob.glob(sys.argv[1])

if len(ms_list) == 0:
    print('There are no files at that location.')
    exit()

# delete the file
try:
    os.remove(output)
except OSError:
    pass

for ms in ms_list:
    # run NDPPP
    os.system('NDPPP msin=' + ms + ' msout=. steps=[count] > ' + text_file)

    # search for the total flagged
    with open(text_file) as f:
        for line in f:
            if the_string in line:
                 save_to_file(ms, line, output)

os.remove(text_file)
