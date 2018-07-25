'''
    Credit: Sean Mooney
    Usage:  # On CEP3, first load ParselTongue:
            $ module load parseltongue
            # Now plot solution tables 5 and 7 from the first entry in your AIPS
            # catalogue, making sure you're referencing UV data and you specify
            # your user number:
            $ ParselTongue plot-solution-tables.py -u 383 --catalogue 0 --sn 5,7
    Detail: This script plots the specified solution tables associated with a
            catalogue entry in AIPS using ParselTongue.
'''

import os
import linecache
import argparse
import numpy             as     np
import matplotlib.pyplot as     plt
from   datetime          import datetime
from   AIPS              import AIPS
from   AIPSTV            import AIPSTV
from   pylab             import plot,       show
from   AIPSTask          import AIPSTask,   AIPSList
from   AIPSData          import AIPSUVData, AIPSImage, AIPSCat
from   Wizardry.AIPSData import AIPSUVData

def plot_sn(user = '', entry = '', disk = 1, chosen_station = [''], FQ = 1, AN = 1, SN = [0], keep = False):

# exit if some conditions are not adhered to -----------------------------------

    if entry == '': print('The catalogue entry of the data is required.'); return
    if user == '': print('The AIPS number of the user is required.'); return
    if len(SN) > 7: print('Too many SN were specified.'); return

# retrieve the data ------------------------------------------------------------

    AIPS.userno = user
    name = AIPSCat()[disk][entry]['name']
    klass = AIPSCat()[disk][entry]['klass']
    seq = AIPSCat()[disk][entry]['seq']
    indata = AIPSUVData(name, klass, disk, seq)

# pull the frequencies of the subbands from the frequency extension table ------

    fq = indata.table('FQ', FQ)
    crval = indata.header['crval'][2]
    nif = len(np.atleast_1d(fq[0]['if_freq']))
    frequencies = np.atleast_1d(fq[0]['if_freq']) + crval

# pull the list of stations from the antenna extension -------------------------

    an = indata.table('AN', AN)
    antennas = []
    stations = []

    for antenna in an:
        antennas.append(antenna['nosta'])
        stations.append(antenna['anname'].strip('HBA').strip('LBA'))

    if chosen_station != ['']:
        print('This feature does not work yet.')
        # stations = chosen_station
        # chosen_joined = ', '.join(chosen_station)
        # if len(chosen_station) == 1:
        #    print('The selected stations is ' + chosen_joined + '.')
        # else:
        #    print('The selected stations are ' + chosen_joined + '.')
    else:
        print('Data for all stations are being plotted.')

# pull information from the solution table and save to a text a file -----------

    sn_string = ''
    sn_data = name + '_SN.txt'

    if os.path.exists(sn_data):
        os.remove(sn_data)
        print('The old ' + sn_data + ' file was deleted.')

    print('The data are being written to ' + sn_data + '.')

    for k in SN:
        sn = indata.table('SN', k)
        sn_string += '-' + str(k)

# lines 87 to 93 were taken from a script by L Morabito ------------------------

        with open(sn_data, 'a+') as f:
            for i in sn:
                if nif == 1:
                    f.write('%s\t%.2f\t%.16f\t%i\t%s\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\n' % (k, frequencies[0], i['time'], i['antenna_no'], stations[i['antenna_no'] - 1], i['delay_1'], i['delay_2'], i['weight_1'], i['weight_2'], i['rate_1'], i['rate_2'], np.arctan2(i['imag1'], i['real1']), np.arctan2(i['imag2'], i['real2'])))
                else:
                    for j in range(nif):
                        f.write('%s\t%.2f\t%.16f\t%i\t%s\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\t%.16f\n' %(k, frequencies[j], i['time'], i['antenna_no'], stations[i['antenna_no'] - 1], i['delay_1'][j], i['delay_2'][j], i['weight_1'][j], i['weight_2'][j], i['rate_1'][j], i['rate_2'][j], np.arctan2(i['imag1'][j], i['real1'][j]), np.arctan2(i['imag2'][j], i['real2'][j])))

# load in the solution table data from the text file ---------------------------

    solution, f, t, antenna, p0, p1 = np.genfromtxt(sn_data, usecols = (0, 1, 2, 4, 5, 6), dtype = str, unpack = True)
    frequency, time, pol0, pol1, pdfs = [], [], [], [], []
    colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']
    total_clipped = 0

    for i in range(len(t)):
        frequency.append(float(f[i]))
        time.append(float(t[i]))
        pol0.append(float(p0[i]))
        pol1.append(float(p1[i]))

# loop through the stations with a new plot for each one -----------------------

    for s in stations:
        station = s.strip(' ')
        plt.figure(figsize = (10, 8))
        plt.title('Polarisation 0 at ' + str(int(frequency[1] * 1e-6)) + ' MHz for ' + station)
        plt.xticks([])
        plt.xlabel('Time')
        plt.ylabel('Delay (ns)')
        q = -1
        clipped = 0

# plot the data for each solution table ----------------------------------------

        for k in SN:
            station_time, station_pol0, station_pol1 = [], [], []
            q += 1

# data clipped in AIPS appears on my plot with value of 3140.892822265625 ------

            for i in range(len(time)):
                if solution[i] == str(k) and frequency[i] == frequency[1] and antenna[i] == station:
                    station_time.append(time[i])

                    if pol0[i] == 3140.892822265625 and i > 0:
                        station_pol0.append(station_pol0[len(station_pol0) - 1])
                        total_clipped += 1
                        clipped += 1

                    elif pol0[i] == 3140.892822265625 and i == 0:
                        station_pol0.append(0)
                        total_clipped += 1
                        clipped += 1

                    else:
                        station_pol0.append(pol0[i] * 1e9)

# actually do the plotting and save the plots when they are all done -----------

            plt.plot(station_time, station_pol0, linewidth = 1, marker = None, color = colors[q], label = 'SN ' + str(k))
            print(str(clipped) + ' points were clipped from SN ' + str(k) + ' for station ' + station + '.')

        plt.legend(loc = 1)
        plt.savefig(station + '-SN.pdf', bbox_inches = 'tight', format = 'pdf')
        pdfs.append(station + '-SN.pdf')
        plt.close()

    print(str(total_clipped) + ' points were clipped in total.\n')

# join the saved plots into one PDF --------------------------------------------

    inputs = ' '.join(pdfs)
    output = name + '-SN' + sn_string + '.pdf'
    print('The transfer is being commenced.')
    make = "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/default -dNOPAUSE -dQUIET -dBATCH -dDetectDuplicateImages -dCompressFonts=true -r150 -sOutputFile=" + output + ' ' + inputs
    os.system(make)

# upload the PDF to transfer.sh ------------------------------------------------

    upload = name + '-SN' + sn_string + '-upload.txt'
    transfer = 'curl --upload-file ' + output + ' https://transfer.sh/' + output + ' > ' + upload
    os.system(transfer)
    line = linecache.getline(upload, 1).rstrip('\n')
    print('\nPaste this into the terminal to retrieve the file:\n')
    print('curl ' + line + ' -o ' + output + '; xdg-open ' + output + '\n')

# delete the working files -----------------------------------------------------

    if keep == False:
        for pdf in pdfs:
            os.remove(pdf)

        os.remove(sn_data)
        os.remove(upload)
        print('The working files were deleted.')
    else:
        print('The working files were not deleted.')

# this is the end of the function ----------------------------------------------

def main():

# define the input arguments ---------------------------------------------------

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', dest = 'user_number', type = int, default = 383, help = 'AIPS user number')
    parser.add_argument('-c', '--catalogue', dest = 'catalogue_entry', type = int, default = '', help = 'Catalogue entry of the data')
    parser.add_argument('-s', '--sn', dest = 'sn_version', type = str, default = 1, help = 'SN versions comma separated without spaces')
    parser.add_argument('-k', '--keep', dest = 'keep_data', type = str, default = False, help = 'Keep the intermediate files')
    parser.add_argument('-a', '--antenna', dest = 'chosen_antenna', type = str, default = '', help = 'Stations comma separated without spaces')

    args = parser.parse_args()
    user_number = args.user_number
    catalogue_entry = args.catalogue_entry
    sn_version = args.sn_version
    sn_version = sn_version.split(',')
    keep_data = args.keep_data
    chosen_antenna = args.chosen_antenna
    chosen_antenna = chosen_antenna.split(',')

    for i in range(len(sn_version)):
        sn_version[i] = int(sn_version[i])

# run the function if the script is executed -----------------------------------

    plot_sn(user = user_number, entry = catalogue_entry, chosen_station = chosen_antenna, SN = sn_version, keep = keep_data)

if __name__ == '__main__':
    main()
