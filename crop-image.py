#!/usr/bin/python

'''
    Credit: Sean Mooney
    Usage: ./crop-image.py
    Detail: Script to crop images to uniform dimensions.
'''

import os
from PIL import Image

folder = '/home/sean/Downloads/lofar' # directory containing images and script
files = len(os.listdir(folder)) - 1 # count images but not the script
w, h = [], []

for i in range(files): # get the dimensions of the images
    if i < 10:
        name = '0' + str(i) + 'n.png'
    else:
        name = str(i) + 'n.png'

    image = Image.open(name)
    w.append(image.size[0])
    h.append(image.size[1])

for i in range(files): # crop images to the smallest dimensions
    if i < 10:
        name = '0' + str(i) + 'n.png'
    else:
        name = str(i) + 'n.png'

    image = Image.open(name)

    cropped = image.crop((0, 0, min(w), min(h)))
    cropped.save(name) # overwrite the old images

print('Images cropped to ' + str(min(w)) + ' x ' + str(min(h)))
