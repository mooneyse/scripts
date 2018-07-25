import os

from AIPS                import AIPS
from AIPSTV              import AIPSTV
from AIPSTask            import AIPSTask,   AIPSList
from AIPSData            import AIPSUVData, AIPSImage
# from Wizardry.AIPSData import AIPSUVData

AIPS.userno = 383

directory   = '/data/scratch/mooney/aips/'
fits        = 'L572667.fits'
show_tv     = 'Yes'

data        = directory + fits
filename    = os.path.basename(data)
name        = os.path.splitext(filename)[0]

def setting_up(observation, tv_switch):
    log = open(directory + name + '.log', 'a+')
    AIPS.log = open(directory + name + '_aips.log', 'a+')
    log.write('* Starting the log file\n')
    log.write('* Opening the AIPS log file too\n')
    log.write('* The %s data are being analysed\n\n' %(observation))   
    tv = AIPSTV()

    if tv_switch == 'Yes':
        log.write('* Turning on the TV\n')
        tv.start()
        log.write('* The TV is on\n')

    else:
        log.write('* The TV is not being switched on\n'

    log.close()

def load_data(datain, outname):
    log = open(directory + name + '.log', 'a+')
    log.write('- Loading the FITS file into AIPS\n'
    log.write('  - Running FITLD\n')
    log.write('    - The file being loaded is %s\n' %(datain))
    log.write('    - The name of the file in AIPS is %s\n' %(outname))
    log.write('    - All other parameters are at the default values\n')
    fitld = AIPSTask('FITLD')
    fitld.datain = datain
    fitld.outname = outname
    fitld.inputs()
    fitld.go()
    log.write('  - FITLD has finished\n\n')
    log.close()

setting_up(fits, show_tv)
load_data(data, name)
