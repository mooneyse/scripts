#!/usr/bin/env python3.7

import urllib.request
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord

url = 'http://www.jb.man.ac.uk/~njj/lbcs_stats.sum'  # don't change
my_ra, my_dec = '08h54m48.8749s', '+20d06m30.641s'  # your pointing centre
results_filename = '/home/sean/Downloads/delay_calibrators.csv'  # please edit
p_threshold = 1

opener = urllib.request.FancyURLopener({})
f = opener.open(url)
content = f.read()
decoded = content.decode('utf-8')
my_list = decoded.splitlines()
lbcs = []

for row in my_list:
    split_row = row.split('  ')
    lbcs.append(split_row)

cols = ['Source_id', 'RA', 'Dec', 'Date', 'Time', 'Goodness', 'X', 'Y', 'Z']
df = pd.DataFrame(lbcs, columns=cols)
df = df.drop(columns=['Date', 'Time', 'X', 'Y', 'Z'])  # don't need these

# remove sources with no flux
num_of_ps = []
for goodness in df['Goodness']:
    p_count = goodness.count('P')  # P is good
    num_of_ps.append(p_count)

df['P_count'] = num_of_ps
df = df[df['P_count'] > p_threshold]  # remove sources with no flux
df = df.drop(columns=['P_count'])  # don't need it any more

lotss_ra, lotss_dec, separations = [], [], []
c1 = SkyCoord(my_ra, my_dec)

for RA, Dec in zip(df['RA'], df['Dec']):
    ra = f"{RA[:2]}h{RA[3:5]}m{RA[6:]}s"
    dec = f"{Dec[:2]}d{Dec[3:5]}m{Dec[6:]}s"
    c2 = SkyCoord(ra, dec)
    sep = c1.separation(c2)
    lotss_ra.append(np.round(c2.ra.degree, 6))
    lotss_dec.append(np.round(c2.dec.degree, 6))
    separations.append(np.round(sep.degree, 4))

df['LOTSS_RA'] = lotss_ra
df['LOTSS_DEC'] = lotss_dec
df['Separation_deg'] = separations
df = df.drop(columns=['RA', 'Dec'])  # don't need these any more
df = df[df['Separation_deg'] < 2]  # remove sources too far away
df = df.sort_values('Separation_deg')  # sort by closest
df = df[['Source_id', 'LOTSS_RA', 'LOTSS_DEC', 'Separation_deg', 'Goodness']]
df.to_csv(results_filename, index=False)
print(f'Done. Check out {results_filename}.')
