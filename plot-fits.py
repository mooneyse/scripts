#!/usr/bin/env python3

'''
    Credit: Sean Mooney
    Usage: ./plot-fits.py fits.fits
    Detail: Plots a fits file image.
'''

# complains that no module 'pyqt4' installed so added these lines as a work around
import matplotlib as mpl
mpl.use('Agg') 

import aplpy, os, sys
import matplotlib.pyplot as plt

try:
    fits = sys.argv[1]
except:
    print('Please supply a fits file.')
    sys.exit(1)
    # fits = '/home/sean/Downloads/images/3C273-run3-low-copy.fits'

plt.rcParams['font.family'] = 'serif'

image = aplpy.FITSFigure(fits)

# image.show_grayscale()
image.show_colorscale(cmap = 'gist_heat')
image.show_contour(fits, colors = 'white')
# ra = [187.2740917, 187.2779167]
# dec = [2.0485000, 2.0525000]
# image.show_markers(ra, dec, edgecolor = 'None', facecolor = '#16A085', marker = '+', s = 500, alpha = 0.8, linewidth = 2)
image.tick_labels.set_font(size = 15)
image.axis_labels.set_font(size = 15)

# plt.show()
image.save(os.path.splitext(fits)[0] + '.eps', format = 'eps')
print('All done! The image is at ' + os.path.splitext(fits)[0] + '.eps')
