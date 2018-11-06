#!/usr/bin/env python

from __future__ import division
from astropy.io import fits
import glob
import os
import subprocess
import sys
import time
import bdsf

ms = '/data5/sean/hba/run3/imaging/data/old/copy/small/new/wsclean-small.ms'
phase_solution_intervals = [38, 2, 1]
phase_number_of_channels = [10, 4, 2]

initial_image = 'poop'
image_prefix = 'source1'

wsclean_phase =  'wsclean -j 12 -mem 80 -scale 0.25asec -baseline-averaging 1400 -no-update-model-required -multiscale -multiscale-gain 0.1 -join-channels -channels-out 2 -mgain 0.7 -auto-threshold 0.3 -local-rms -niter 10000 -size 1024 1024 -weight briggs -1 -minuv-l 4000 -data-column CORRECTED_DATA_PHASE_ONLY -casa-mask {mask} -name {imgbase}_selfcal_p{i} {ms}'
wsclean_predict = 'wsclean -j 12 -mem 80 -scale 0.25asec -predict -channels-out 2 -mgain 0.7 -auto-mask 3 -auto-threshold 0.3 -local-rms -niter 10000 -size 1024 1024 -weight briggs -1 -name {imgbase}_selfcal_p{i} {ms}'

PHASE_PARSET = '''numthreads = 12
msin = {msin}
msout = .
msout.datacolumn = CORRECTED_DATA_PHASE_ONLY
msout.storagemanager = dysco

steps = [phasecal]

phasecal.type           = gaincal
phasecal.caltype        = phaseonly
phasecal.usemodelcolumn = true
phasecal.parmdb         = {img}_selfcal_p{i}.h5
phasecal.uvmmin         = 4000
phasecal.solint         = {solint}
phasecal.nchan          = {nchan}
phasecal.applysolution  = true'''

LOSOTO_PLOT_PARSET = '''Ncpu = 12
soltab = [sol000/phase000]
dir = [pointing]
pol = [XX, YY]

[plot_phase]
operation   = PLOT
axesInPlot  = [time]
axisInTable = ant
prefix      = source4_selfcal{i}_raw_phase
soltab      = sol000/phase000
minmax      = [-3.14, 3.14]'''

'''
[plot_phase2]
operation   = PLOT
axesInPlot  = [time,freq]
axisInTable = ant
minmax      = [-3.14, 3.14]
prefix      = {img}_selfcal{i}_raw_phase
soltab      = sol000/phase000'''
def measure_statistic(fitsname):
    # Assume a single image (no cube).
    img = fits.open(fitsname)[0].data.squeeze()
    imin = img.min()
    imax = img.max()
    statistic = abs(imax / imin)
    return statistic

## Commence self-calibration loop.
# Phase-only
print('Starting phase-only self-calibration.')
for i,s,c in zip(range(1,len(PSOLINTS)+1), PSOLINTS, PNCHANS):
    print('Iteration {i}'.format(i=i))
    if os.path.isfile('source4_selfcal_p{i}.h5'.format(i=i)):
        print('NDPPP for iteration {i} already run.'.format(i=i))
    else:
        if i == 1 and (INITIAL_IMAGE is not None):
            predict = 'wsclean -j 12 -mem 80 -scale 0.25asec -predict -channels-out 2 -mgain 0.7 -auto-mask 3 -auto-threshold 0.3 -local-rms -niter 10000 -size 1024 1024 -weight briggs -1 -name {img} {ms}'
            print('First iteration, predicting INITIAL_IMAGE.')
            subprocess.check_output(predict.format(i=i, ms=ms, img=INITIAL_IMAGE), shell=True)
        print('Starting phase-only selfcalibration with NDPPP...')
        # Fill in the relevant parameters in the parset.
        parset = PHASE_PARSET.format(msin=ms, img=IMAGE_BASENAME, i=i, solint=s, nchan=c)
        parset_file = 'selfcal{i}.parset'.format(i=i)
        with open(parset_file, 'w') as f:
            f.write(parset)
        # Run NDPPP selfcal.
        time_start = time.time()
        subprocess.check_output(['NDPPP', parset_file])
        time_end = time.time()
        print('Step NDPPP finished in {:.2f} s.'.format((time_end - time_start)))

    # Make plots with LoSoTo.
    if glob.glob('{img}_selfcal{i}*.png'.format(img=IMAGE_BASENAME, i=i)) > 0:
        print('LoSoTo for iteration {i} already run.'.format(i=i))
    else:
        print('Starting LoSoTo plotting...')
        time_start = time.time()
        with open('losoto_plot.parset', 'w') as f:
            f.write(LOSOTO_PLOT_PARSET.format(img=IMAGE_BASENAME, i=i))
        subprocess.check_output('/usr/bin/losoto {img}_selfcal_p{i}.h5 losoto_plot.parset'.format(img=IMGAGE_BASENAME, i=i), shell=True)
        time_end = time.time()
        print('Step LoSoTo finished in {:.2f} s.'.format((time_end - time_start)))

    # Run WSCLEAN to obtain a new model.
    time_start = time.time()
    if os.path.isfile('source4_selfcal_p{i}-MFS-image.fits'.format(i=i)):
        print('WSClean for iteration {i} already run.'.format(i=i))
    else:
        print('Imaging and processing with PyBDSF...')
        # Make PyBDSF mask.
        if i == 1 and (INITIAL_IMAGE is not None):
            subprocess.check_output(WSCLEAN_PHASE.format(i=i, ms=ms, imgbase=IMAGE_BASENAME, mask='blank3.mask'), shell=True)
        elif  i > 1:
            subprocess.check_output(WSCLEAN_PHASE.format(i=i, ms=ms, imgbase=IMAGE_BASENAME, mask='blank3.mask'), shell=True)
        # Measure the statistic for image quality.
        if i == 1 and (INITIAL_IMAGE is not None):
            previous = measure_statistic(INITIAL_IMAGE + '-MFS-image.fits')
        elif i > 1:
            previous = measure_statistic('{imgbase}_selfcal_p{i}-MFS-image.fits'.format(i=(i-1), imgbase=IMAGE_BASENAME))
        current = measure_statistic('{imgbase}_selfcal_p{i}-MFS-image.fits'.format(i=i, imgbase=IMAGE_BASENAME))
        if (current - previous) < 0 and i > 1:
            print('Image quality reducing, applying previous solutions and stopping phase-only self-calibration.')
            print('Best result: {img}'.format(img='phaseshift_selfcal_p{i}-robust-n1-baselavg-deep-MFS-image.fits'.format(i=(i-1))))
            subprocess.check_output('NDPPP msin={msin} msout=. msout.datacolumn=CORRECTED_DATA_PHASE_ONLY msout.storagemanager=dysco steps=[applycal] applycal.type=applycal applycal.parmdb={h5parm} applycal.correction=phase000'.format(msin=MSFILE, h5parm='{img}_selfcal_p{i}.h5'.format(img=IMAGE_BASENAME, i=i-1)), shell=True)
            break
        elif (current - previous) < 0 and i == 1:
            print('Image quality reducing, stopping phase-only self-calibration.')
            print('Please re-apply previous solutions before continueing.')
            break
        elif (current - previous) > 0 and (current - previous) < 0.01:
            print('No further improvement, stopping phase-only self-calibration.')
            print('Best result: {img}'.format(img='phaseshift_selfcal_p{i}-robust-n1-baselavg-deep-MFS-image.fits'.format(i=(i-1))))
            break
        else:
            print('Image quality improved. Writing back model and continuing self-calibration.')
            subprocess.check_output(WSCLEAN_PREDICT.format(i=i, msfile=MSFILE, imgbase=IMAGE_BASENAME), shell=True)
        time_end = time.time()
        print('Step WSClean finished in {:.2f} s.'.format((time_end - time_start)))
    print
