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

# the last step in the long-baseline pipeline parset wrote to the CORRECTED_DATA column

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
imsize           = round(image_x_and_y / cell) # calculate image size (high resolution is 899 pixels, low resolution is 240 pixels)

''' self-calibration round 1 ----------------------------------------------- '''

# achievable noise = 34.96 μJy/beam (LOFAR sensitivity calculator excludes weather conditions and target source)
# stop cleaning when residuals become noise-like but still be a bit conservative, especially for weak features
# you cannot get rid of real emission by not boxing it but you can create features by boxing noise

# try uniform weighting and appropriate uv cuts without multiscale first
# it'll be easier to make 2 images using uv cuts, 1 high and 1 low resolution
# then feather them together like in Varenius+ (2015)

# exportuvfits.last
taskname           = "exportuvfits"
vis                =  "/data5/sean/hba/run3/imaging/ms3-fill-missing-data.ms/"
fitsfile           =  "/data5/sean/hba/run3/imaging/ms3-fill-missing-data.fits"
datacolumn         =  "data"
field              =  ""
spw                =  ""
antenna            =  ""
timerange          =  ""
writesyscal        =  False
multisource        =  False
combinespw         =  True
writestation       =  True
padwithflags       =  True
overwrite          =  False

tclean(                                  # do the cleaning
    vis         = '/data5/sean/hba/run1/imaging/ms1-110-datacol.ms', # two rounds of cleaning done
    imagename   = '3c273-test',           #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines
    cell        = [0.1473],              #
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True)#,                  #
    savemodel   = 'modelcolumn')         # model is required for later self-calibration steps

tclean(                                  # do the cleaning
    vis         = '/data5/sean/hba/runs13/data/concatenate-110.ms',               # two rounds of cleaning done
    imagename   = '3c273-1',           #
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [899, 899],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines
    cell        = ['0.0393arcsec'],              #
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')         # model is required for later self-calibration steps


imview(                                  # view the cleaned image
    raster      = '3C273-l-1.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

# I can see the jet head which I cleaned but the source isn't there!

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

# had interp = 'linearperobs' but only 1 observation so it ignored this interpolation.

''' self-calibration round 2 ----------------------------------------------- '''

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               # two rounds of cleaning done
    imagename   = '3C273-l-2',           #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines
    cell        = [0.1473],              #
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')         # model is required for later self-calibration steps

# did one round then exited without placing any boxes because I had to leave
# picked it up again the next day and did two rounds, placing boxes

imview(                                  # view the cleaned image
    raster      = '3C273-l-2.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

# I can see the jet head which I cleaned but the source isn't there!

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
    vis         = 'ms.ms',               # two rounds of cleaning done
    imagename   = '3C273-l-3',           #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines
    cell        = [0.1473],              #
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')         # model is required for later self-calibration steps

imview(                                  # view the cleaned image
    raster      = '3C273-l-3.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

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

''' self-calibration round 4 ----------------------------------------------- '''

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               # two rounds of cleaning done
    imagename   = '3C273-l-4',           #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines
    cell        = [0.1473],              #
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')         # model is required for later self-calibration steps

imview(                                  # view the cleaned image
    raster      = '3C273-l-4.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

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

''' > here '''

tclean(                                  # do the cleaning
    vis         = 'ms.ms',               #
    imagename   = '3C273-l-5',           #
    uvrange     = '0~200klambda',        # low resolution image
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [240, 240],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines
    cell        = [0.1473],              #
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -1.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '0mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True)                  #

imview(                                  # view the cleaned image
    raster      = '3C273-l-5.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

# compare previous image with this amplitude self-calibration image
# compare S/N = (peak Jy/beam)/(rms Jy/beam)

''' export from CASA ------------------------------------------------------- '''

exportfits(                              # casa images can be exported as fits files
    imagename = '3C273-l-5.image.tt0',   #
    fitsimage = '3C273-l.fits')          #

''' use APLpy to make it of publication quality ---------------------------- '''

# use Astropy for contours
