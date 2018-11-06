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

# clean I ran with Lean in Leiden at the SKSP meeting
#clean(vis="/data5/sean/hba/run3/imaging/ms.ms",imagename="3c273-run3-lowres",outlierfile="",field="",spw="0:10~60",selectdata=True,timerange="",uvrange=">80klambda",antenna="",scan="",observation="",intent="",mode="mfs",resmooth=False,gridmode="",wprojplanes=-1,facets=1,cfcache="cfcache.dir",rotpainc=5.0,painc=360.0,aterm=True,psterm=False,mterm=True,wbawp=False,conjbeams=True,epjtable="",interpolation="linear",niter=5000,gain=0.1,threshold="0mJy",psfmode="clark",imagermode="csclean",ftmachine="mosaic",mosweight=False,scaletype="SAULT",multiscale=[0],negcomponent=-1,smallscalebias=0.6,interactive=True,mask=[],nchan=-1,start=0,width=1,outframe="",veltype="radio",imsize=[240, 240],cell=['0.04arcsec'],phasecenter="",restfreq="",stokes="I",weighting="briggs",robust=-2.0,uvtaper=False,outertaper=[''],innertaper=['1.0'],modelimage="",restoringbeam=[''],pbcor=True,minpb=0.2,usescratch=False,noise="1.0Jy",npixels=0,npercycle=10,cyclefactor=1.5,cyclespeedup=-1,nterms=1,reffreq="",chaniter=False,flatnoise=True,allowchunk=False)

# when the data outputted from the lb pipeline were concatenated, the corrected data were copied to the data column

tclean(                                  # do the cleaning
    vis         = 'nov-again.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [2000, 2000],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')
'''NOV here placed one clean box on the jet head. 10 max cycleniter, 0.01jy threshold, cyclethreshold 0.420181'''
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

'''{'blc': array([0, 0, 0, 0], dtype=int32),
 'blcf': '12:29:07.880, +02.02.51.015, I, 1.50494e+08Hz',
 'flux': array([ 3.83063034]),
 'max': array([ 1.40856409]),
 'maxpos': array([759, 120,   0,   0], dtype=int32),
 'maxposf': '12:29:05.890, +02.02.55.731, I, 1.50494e+08Hz',
 'mean': array([ 0.00036116]),
 'medabsdevmed': array([ 0.0309557]),
 'median': array([  7.38790914e-05]),
 'min': array([-0.30088311]),
 'minpos': array([756, 253,   0,   0], dtype=int32),
 'minposf': '12:29:05.898, +02.03.00.958, I, 1.50494e+08Hz',
 'npts': array([ 810000.]),
 'q1': array([-0.03097994]),
 'q3': array([ 0.03092873]),
 'quartile': array([ 0.06190866]),
 'rms': array([ 0.04949074]),
 'sigma': array([ 0.04948945]),
 'sum': array([ 292.5413548]),
 'sumsq': array([ 1983.95997948]),
 'trc': array([899, 899,   0,   0], dtype=int32),
 'trcf': '12:29:05.523, +02.03.26.346, I, 1.50494e+08Hz'}
'''

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-1',        # name for the calibration table generated
    #uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'p',                   # phase only
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '240s')                # want it to be short enough to track changes in the atmospheric phase with high accuracy but long enough to measure phases with good signal-to-noise

# if there are lots of failed solutions on most antennas, go back and increase S/N of solution = more averaging of some kind
# calibration solve statistics (spw - expected/attempted/succeeded): spw 0 - 60/52/52

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-1',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

'''nov: flagged one point on PL station'''

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-1'])      #

''' self-calibration round 2 ----------------------------------------------- '''

tclean(                                  # do the cleaning
    vis         = 'nov-small.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-2',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [900, 900],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')


imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-2.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

imstat(
    imagename   = '3c273-run3-lowres-2.image.tt0')

'''
{'blc': array([0, 0, 0, 0], dtype=int32),
 'blcf': '12:29:07.880, +02.02.51.015, I, 1.50494e+08Hz',
 'flux': array([ 5.19990935]),
 'max': array([ 1.55964482]),
 'maxpos': array([759, 120,   0,   0], dtype=int32),
 'maxposf': '12:29:05.890, +02.02.55.731, I, 1.50494e+08Hz',
 'mean': array([ 0.00049606]),
 'medabsdevmed': array([ 0.0399086]),
 'median': array([ -3.57224781e-05]),
 'min': array([-0.29694822]),
 'minpos': array([759, 323,   0,   0], dtype=int32),
 'minposf': '12:29:05.890, +02.03.03.709, I, 1.50494e+08Hz',
 'npts': array([ 810000.]),
 'q1': array([-0.03989076]),
 'q3': array([ 0.03992301]),
 'quartile': array([ 0.07981377]),
 'rms': array([ 0.06130784]),
 'sigma': array([ 0.06130587]),
 'sum': array([ 401.80769623]),
 'sumsq': array([ 3044.50713954]),
 'trc': array([899, 899,   0,   0], dtype=int32),
 'trcf': '12:29:05.523, +02.03.26.346, I, 1.50494e+08Hz'}
'''

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-2',        # name for the calibration table generated
    #uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'p',                   # phase only
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '30s')                 # want it to be short enough to track changes in the atmospheric phase with high accuracy but long enough to measure phases with good signal-to-noise

''' # calibration solve statistics (spw - expected/attempted/succeeded): spw 0 - 480/416/416 '''

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
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-2'])      #

''' self-calibration round 3 ----------------------------------------------- '''

tclean(                                  # do the cleaning
    vis         = 'nov-small.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-3',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [900, 900],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

'''nov; here! issue is there is no bloody core!!!'''

imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-3.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

imstat(
    imagename   = '3c273-run3-lowres-3.image.tt0')

# {'blc': array([0, 0, 0, 0], dtype=int32),
#  'blcf': '12:29:07.880, +02.02.51.015, I, 1.50494e+08Hz',
#  'flux': array([ 3.8578088]),
#  'max': array([ 1.84218645]),
#  'maxpos': array([759, 120,   0,   0], dtype=int32),
#  'maxposf': '12:29:05.890, +02.02.55.731, I, 1.50494e+08Hz',
#  'mean': array([ 0.00036602]),
#  'medabsdevmed': array([ 0.05933845]),
#  'median': array([ 0.00012361]),
#  'min': array([-0.48008484]),
#  'minpos': array([762, 254,   0,   0], dtype=int32),
#  'minposf': '12:29:05.882, +02.03.00.997, I, 1.50494e+08Hz',
#  'npts': array([ 810000.]),
#  'q1': array([-0.05951405]),
#  'q3': array([ 0.05916906]),
#  'quartile': array([ 0.11868311]),
#  'rms': array([ 0.08851677]),
#  'sigma': array([ 0.08851606]),
#  'sum': array([ 296.47601197]),
#  'sumsq': array([ 6346.52658607]),
#  'trc': array([899, 899,   0,   0], dtype=int32),
#  'trcf': '12:29:05.523, +02.03.26.346, I, 1.50494e+08Hz'}


# compare previous image with this phase-only self-calibration image
# compare S/N = (peak Jy/beam)/(rms Jy/beam)
# if it did not improve, try amplitude self-calibration next

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-3',        # name for the calibration table generated
    # uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'p',                   # phase only
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '4s')                  # want it to be short enough to track changes in the atmospheric phase with high accuracy but long enough to measure phases with good signal-to-noise

''' # calibration solve statistics (spw - expected/attempted/succeeded): spw 0 - 3600/3092/2977 '''

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-3',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

smoothcal(
vis          =         'nov-small.ms'  , #  Name of input visibility file
tablein      =          'caltable-l-3' , #  Input calibration table
caltable     =         'caltable-l-3-smoo'  , #,  Output calibration table
#field        =         ''   ,#  Field name list
smoothtype   =   'median'  , #  Smoothing filter to use
smoothtime   =       60.0 ,  #  Smoothing time (sec)
#async        =      False   #  if True run in the background, prompt is freed
)

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-3-smoo',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-3-smoo'])      #

''' self-calibration round 4 ----------------------------------------------- '''

# plotms(
#     vis = 'ms.ms',
#     xaxis = 'time', # 'frequency'
#     yaxis = 'amplitude', # 'phase'
#     ydatacolumn = 'corrected',
#     antenna = '*&',
#     correlation = 'XX',
#     plotfile='test.png',
#     expformat 'png',
#     exprange = 'all',
#     overwrite = 'True',
#     showgui = 'False',
#     iteraxis = 'antenna',
#     customflaggedsymbol = True,
#     flaggedsymbolshape = 'circle',
#     flaggedsymbolsize = 5,
#     flaggedsymbolcolor = 'ff0000',
#     flaggedsymbolfill = 'fill')

'''HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 02 nov 2018'''

tclean(                                  # do the cleaning
    vis         = 'nov-small.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-4',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [900, 900],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-4.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-4',        # name for the calibration table generated
    #uvrange     = '0~200klambda',        # low resolution image
    gaintype    = 'T',                   # average polarisations
    calmode     = 'p',                   # phase only
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '80s')                 # want it

# gaincal(                                 # determine temporal gains
#     vis         = 'ms.ms',               # my measurement set
#     caltable    = 'caltable-l-4',        # name for the calibration table generated
#     uvrange     = '0~200klambda',        # low resolution image
#     gaintype    = 'T',                   # average polarisations
#     calmode     = 'ap',                  # amplitude and phase
#     combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
#     solint      = '1200s')               # amplitude varies more slowly than phase and is less constrained so solint are longer

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-4',        #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

# make sure mostly good solutions and a smoothly varying pattern

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-4'])      #

tclean(                                  # do the cleaning
    vis         = 'nov-small.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-run3-lowres-5',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [900, 900],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

'''here'''
imview(                                            # view the cleaned image
    raster      = '3c273-run3-lowres-5.image.tt0') # .tt0 is the total intensity image, equivalent to .image from standard imaging

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-amp1',        # name for the calibration table generated
    gaintype    = 'T',                   # average polarisations
    calmode     = 'ap',                  # amplitude and phase
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '1200s')               # amp

# TELL NB NB NB LEAH that the solutions don't look smooth at less than 2 minutes

plotcal(                                 # do the phases appear smoothly varying with time as opposed to noise-like?
    caltable    = 'caltable-l-amp1',  #
    xaxis       = 'time',                #
    yaxis       = 'phase',               #
    iteration   = 'antenna',             #
    subplot     = 421,                   #
    plotrange   = [0, 0, -180, 180])     #

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-amp1'])

tclean(                                  # do the cleaning
    vis         = 'nov-small.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-ampl1',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [900, 900],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

imview(                                            # view the cleaned image
    raster      = '3c273-ampl1.image.tt0') # .t

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-amp2',        # name for the calibration table generated
    gaintype    = 'T',                   # average polarisations
    calmode     = 'ap',                  # amplitude and phase
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '1200s')               # amp

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-amp2'])

tclean(                                  # do the cleaning
    vis         = 'nov-small.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-ampl2',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [900, 900],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-amp3',        # name for the calibration table generated
    gaintype    = 'T',                   # average polarisations
    calmode     = 'ap',                  # amplitude and phase
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '1200s')


applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-amp3'])

tclean(                                  # do the cleaning
    vis         = 'nov-small.ms',        # changed name I think as was too long a string for AIPS
    imagename   = '3c273-ampl3',   #
    #uvrange     = '0~200klambda',        # low resolution image - would've made an >80k lambda cut but the CS are tied
    specmode    = 'mfs',                 # multifrequency synthesis mode
    deconvolver = 'mtmfs',               # Multi-term (Multi Scale) Multi-Frequency Synthesis
    nterms      = 2,                     # 2 is a good starting point for wideband low frequency imaging and if there is a bright source for which a dynamic range of greater than ~100 is desired
    gridder     = 'standard',            #
    imsize      = [900, 900],            # number of pixels must be even and factorizable by 2, 3, 5, or 7 to take advantage of internal FFT routines (900 for high res)
    cell        = ['0.0393arcsec'],      # 0.0393arcsec for high res
    weighting   = 'briggs',              # Briggs with robust = -2 is uniform, robust = 2 is natural
    robust      = -2.0,                  # robust = -2 for high resolution, robust = -1 for low resolution
    threshold   = '10mJy',                # stops when max residual in tclean region < threshold
    niter       = 5000,                  #
    pbcor       = True,                  # the output needs to be divided by the primary beam to form an astronomically correct image of the sky
    interactive = True,                  #
    savemodel   = 'modelcolumn')

gaincal(                                 # determine temporal gains
    vis         = 'nov-small.ms',               # my measurement set
    caltable    = 'caltable-l-amp4',        # name for the calibration table generated
    gaintype    = 'T',                   # average polarisations
    calmode     = 'ap',                  # amplitude and phase
    combine     = 'spw',                 # average spectral windows - if source spectral index/morphology changes significantly across the band, do not combine spws, especially for amplitude
    solint      = '1200s')

applycal(                                # apply the calibration to the data for next round of imaging
    vis         = 'nov-small.ms',               #
    gaintable   = ['caltable-l-amp4'])

''' evaluate the calibration ----------------------------------------------- '''

plotms(                                          # look at the uv coverage
    vis                 = 'ms.ms',               #
    xaxis               = 'uvwave',              #
    yaxis               = 'amplitude' ,          #
    antenna             = '*&',
    correlation         = 'XX',
    plotfile            = 'test.png',
    expformat           = 'png',
    exprange            = 'all',
    overwrite           = 'True',
    showgui             = 'False',
    iteraxis            = 'antenna',
    customflaggedsymbol = True,
    flaggedsymbolshape  = 'circle',
    flaggedsymbolsize   = 5,
    flaggedsymbolcolor  = 'ff0000',
    flaggedsymbolfill   = 'fill')

# NOTE here 12:04 18-09-2018

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

''' export from casa ------------------------------------------------------- '''

exportfits(                                        # casa images can be exported as fits files
    imagename = '3c273-run3-lowres-5.image.tt0',   #
    fitsimage = '3C273-l.fits')                    #

''' use APLpy to make it of publication quality ---------------------------- '''

# use astropy for contours
