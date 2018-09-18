''' useful links ----------------------------------------------------------- '''

# https://github.com/aakepley/ALMAImagingScript/blob/master/scriptForImaging_template.py
# http://docs.astropy.org/en/stable/visualization/wcsaxes/images_contours.html
# http://adsabs.harvard.edu/abs/2015A%26A...574A.114V
# https://casaguides.nrao.edu/index.php/VLA_CASA_Imaging-CASA5.0.0
# https://casaguides.nrao.edu/index.php/Self-Calibration_Template
# https://science.nrao.edu/facilities/alma/naasc-workshops/nrao-cd-wm16/Selfcal_Madison.pdf
# https://support.astron.nl/ImageNoiseCalculator/sens.php
# https://casaguides.nrao.edu/index.php/First_Look_at_Self_Calibration

''' impor stuff ------------------------------------------------------------ '''

import aplpy, glob, numpy, os
from astropy.io import fits

''' prepare the data ------------------------------------------------------- '''

# the last step in the long-baseline pipeline parset wrote to the corrected_data column

os.system('cp -r output/long-baseline/L* imaging/data/')                   # copy in case things go wrong
os.system('msoverview in=L606014_SB028_uv.ndppp_prep_target verbose=True') # find the time and frequency averaging
os.system('casabrowser')                                                   # inspect the MS
os.system('NDPPP averaging.parset')                                        # concatenate data and average to 4 seconds and 4 channels/subband from 2 seconds and 16 channels/subband

''' calculate parameters --------------------------------------------------- '''

os.system('./fix-columns.py ms.ms SIGMA')      # correct the SIGMA column
os.system('./fix-columns.py ms.ms WEIGHT')     # correct the WEIGHT column

plotms(                                        # look at the uv coverage
    vis          = 'ms.ms',                    # my measurement set
    xaxis        = 'uvwave',                   # distance in wavelengths on x-axis
    yaxis        = 'amplitude',                # amplitude on y-axis
    avgchannel   = '4',                        # from 4 channels/subband to 1 channel/subband
    avgtime      = '64')                       # from 4 seconds to 256 seconds

longest_baseline = 749000                      # from plotms (high resolution is 749000 wavelengths, low resolution is 200000 wavelengths)
resolution       = 206265 / longest_baseline   # high resolution is 0.2754 arcseconds, low resolution is 1.0313 arcseconds
cell             = resolution / 7              # calculate cell size (high resolution is 0.0393 arcseconds, low resolution is 0.1473 arcseconds)

image_diagonal   = 50                          # arcseconds
image_x_and_y    = image_diagonal / np.sqrt(2) # 35.3553 arcseconds
imsize           = round(image_x_and_y / cell) # calculate image size (high resolution is 899 - i.e., 900 - pixels, low resolution is 240 pixels)

exportuvfits(
    vis          =  'ms3-fill-missing-data.ms',   # if it is to be taken into aips (directory: /data5/sean/hba/run3/imaging/)
    fitsfile     =  'ms3-fill-missing-data.fits',
    datacolumn   =  'data',                       # note - not corrected data
    field        =  '',
    spw          =  '',
    antenna      =  '',
    timerange    =  '',
    writesyscal  =  False,
    multisource  =  False,
    combinespw   =  True,
    writestation =  True,
    padwithflags =  True,
    overwrite    =  False)

''' self-calibration round 1 ----------------------------------------------- '''

# achievable noise = 34.96 μJy/beam (LOFAR sensitivity calculator excludes weather conditions and target source)
# stop cleaning when residuals become noise-like but still be a bit conservative, especially for weak features
# you cannot get rid of real emission by not boxing it but you can create features by boxing noise

# try uniform weighting and appropriate uv cuts without multiscale first
# it'll be easier to make 2 images using uv cuts, 1 high and 1 low resolution
# then feather them together like in varenius+ (2015)

# when the data outputted from the lb pipeline were concatenated, the corrected data were copied to the data column

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres',   #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.1473arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

# placed two clean boxes, one around the core and one around the jet - then clicked the green arrow circle
# did not place any new boxes and then clicked the red x

# see https://casa.nrao.edu/casadocs-devel/stable/global-task-list/task_imstat/about for column explanation
# {'blc': array([0, 0, 0, 0], dtype=int32),
#  'blcf': '12:29:07.879, +02.02.51.024, I, 1.544e+08Hz',
#  'flux': array([ 3.14327833]),
#  'max': array([ 1.80774069]),
#  'maxpos': array([202,  32,   0,   0], dtype=int32),
#  'maxposf': '12:29:05.894, +02.02.55.738, I, 1.544e+08Hz',
#  'mean': array([ 0.00145247]),
#  'medabsdevmed': array([ 0.06836495]),
#  'median': array([-0.00014482]),
#  'min': array([-0.51338387]),
#  'minpos': array([200,  11,   0,   0], dtype=int32),
#  'minposf': '12:29:05.914, +02.02.52.644, I, 1.544e+08Hz',
#  'npts': array([ 57600.]),
#  'q1': array([-0.06885381]),
#  'q3': array([ 0.06783679]),
#  'quartile': array([ 0.1366906]),
#  'rms': array([ 0.10373937]),
#  'sigma': array([ 0.1037301]),
#  'sum': array([ 83.66239431]),
#  'sumsq': array([ 619.88296805]),
#  'trc': array([239, 239,   0,   0], dtype=int32),
#  'trcf': '12:29:05.531, +02.03.26.229, I, 1.544e+08Hz'}

imview(                                          # view the cleaned image
    raster      = '3c273-run3-lowres.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

imstat(
    imagename   = '3c273-run3-lowres.image.tt0')

gaincal(                                 # determine temporal gains
    vis         = 'ms.ms',               # my measurement set
    caltable    = 'caltable-l-1',        # name for the calibration table generated
    uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'p',                   # phase only
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '240s')                # want it to be short enough to track changes in the atmospheric phase with high accuracy but long enough to measure phases with good signal-to-noise

# if there are lots of failed solutions on most antennas, go back and increase S/N of solution = more averaging of some kind
# calibration solve statistics (spw - expected/attempted/succeeded): spw 0 - 60/60/60

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-1',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'ms.ms',               #
    gaintable   = ['caltable-l-1'])      #

''' self-calibration round 2 ----------------------------------------------- '''

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-2', #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.1473arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-2.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

imstat(
    imagename   = '3c273-run3-lowres-2.image.tt0')

# {'blc': array([0, 0, 0, 0], dtype=int32),
#  'blcf': '12:29:07.879, +02.02.51.024, I, 1.544e+08Hz',
#  'flux': array([-85.11868151]),
#  'max': array([ 1.09920049]),
#  'maxpos': array([202,  32,   0,   0], dtype=int32),
#  'maxposf': '12:29:05.894, +02.02.55.738, I, 1.544e+08Hz',
#  'mean': array([-0.04013596]),
#  'medabsdevmed': array([ 0.0311427]),
#  'median': array([-0.04206826]),
#  'min': array([-0.33108622]),
#  'minpos': array([202,  50,   0,   0], dtype=int32),
#  'minposf': '12:29:05.894, +02.02.58.389, I, 1.544e+08Hz',
#  'npts': array([ 57600.]),
#  'q1': array([-0.07241488]),
#  'q3': array([-0.01005821]),
#  'quartile': array([ 0.06235667]),
#  'rms': array([ 0.06646583]),
#  'sigma': array([ 0.05297981]),
#  'sum': array([-2311.83126209]),
#  'sumsq': array([ 254.45991607]),
#  'trc': array([239, 239,   0,   0], dtype=int32),
#  'trcf': '12:29:05.531, +02.03.26.229, I, 1.544e+08Hz'}

gaincal(                                 # determine temporal gains
    vis         = 'ms.ms',               # my measurement set
    caltable    = 'caltable-l-2',        # name for the calibration table generated
    uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'p',                   # phase only
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '30s')                 # want it to be short enough to track changes in the atmospheric phase with high accuracy but long enough to measure phases with good signal-to-noise

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-2',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

# if this looks noisy, go back and stick with longer solint
# if it improves things a lot, try an even shorter solint

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'ms.ms',               #
    gaintable   = ['caltable-l-2'])      #

''' self-calibration round 3 ----------------------------------------------- '''

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-3', #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.1473arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-3.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

imstat(
    imagename   = '3c273-run3-lowres-3.image.tt0')

# {'blc': array([0, 0, 0, 0], dtype=int32),
#  'blcf': '12:29:07.879, +02.02.51.024, I, 1.544e+08Hz',
#  'flux': array([-77.91278479]),
#  'max': array([ 1.41481519]),
#  'maxpos': array([202,  32,   0,   0], dtype=int32),
#  'maxposf': '12:29:05.894, +02.02.55.738, I, 1.544e+08Hz',
#  'mean': array([-0.03687202]),
#  'medabsdevmed': array([ 0.03006466]),
#  'median': array([-0.03980701]),
#  'min': array([-0.50950491]),
#  'minpos': array([199,  17,   0,   0], dtype=int32),
#  'minposf': '12:29:05.924, +02.02.53.528, I, 1.544e+08Hz',
#  'npts': array([ 57600.]),
#  'q1': array([-0.06885893]),
#  'q3': array([-0.00853507]),
#  'quartile': array([ 0.06032386]),
#  'rms': array([ 0.0684131]),
#  'sigma': array([ 0.05762694]),
#  'sum': array([-2123.82828518]),
#  'sumsq': array([ 269.58831972]),
#  'trc': array([239, 239,   0,   0], dtype=int32),
#  'trcf': '12:29:05.531, +02.03.26.229, I, 1.544e+08Hz'}

# compare previous image with this phase-only self-calibration image
# compare S/N = (peak Jy/beam)/(rms Jy/beam)
# if it did not improve, try amplitude self-calibration next

gaincal(                                 # determine temporal gains
    vis         = 'ms.ms',               # my measurement set
    caltable    = 'caltable-l-3',        # name for the calibration table generated
    uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'p',                   # phase only
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '4s')                  # want it to be short enough to track changes in the atmospheric phase with high accuracy but long enough to measure phases with good signal-to-noise

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-3',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'ms.ms',               #
    gaintable   = ['caltable-l-3'])      #

# NOTE here 00:18 18:09:2018

''' self-calibration round 4 ----------------------------------------------- '''

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-4', #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.1473arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-4.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

gaincal(                                 # determine temporal gains
    vis         = 'ms.ms',               # my measurement set
    caltable    = 'caltable-l-4',        # name for the calibration table generated
    uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'ap',                  # amplitude and phase
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '1200s')               # amplitude varies more slowly than phase and is less constrained so solint are longer

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-4',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

# make sure mostly good solutions and a smoothly varying pattern

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'ms.ms',               #
    gaintable   = ['caltable-l-4'])      #

''' evaluate the calibration ----------------------------------------------- '''

plotms(                                  # look at the uv coverage
    vis         = 'ms.ms',               #
    xaxis       = 'uvwave',              #
    yaxis       = 'amplitude')           #

# inspect the uv plot of corrected data to check for any new outliers
# if there are some, flag them and go back to before the amplitude calibration cycle
# make sure the model is good match to data
# confirm that flux has not decreased significantly after applying solutions

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-5', #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.1473arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-5.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

# compare previous image with this amplitude self-calibration image
# compare S/N = (peak Jy/beam)/(rms Jy/beam)

''' export from CASA ------------------------------------------------------- '''

exportfits(                                        # casa images can be exported as fits files
    imagename = '3c273-run3-lowres-5.image.tt0',   #
    fitsimage = '3C273-l.fits')                    #

''' use APLpy to make it of publication quality ---------------------------- '''

# use astropy for contours
