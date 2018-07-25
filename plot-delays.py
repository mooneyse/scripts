
## 1 Plotting AIPS and CASA delays

### 1.1 Import modules

import os
import numpy as np
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileMerger


### 1.2 Load the data

#### 1.2.1 Get the CASA data

w, x, y, z = np.loadtxt('casa.txt', delimiter=' ', usecols = (0, 1, 2, 3), unpack = True)

#### 1.2.2 Get the AIPS data

f, t, a, p1, p2 = np.genfromtxt('aips.txt', usecols = (0, 1, 3, 4, 5), dtype = str, unpack = True)

frequency = []
time = []
antenna = []
pol1 = []
pol2 = []

for i in range(len(t)):
    frequency.append(float(f[i]))
    time.append(float(t[i]))
    antenna.append(a[i])
    pol1.append(float(p1[i]))
    pol2.append(float(p2[i]))


### 1.3 A spot of house-keeping

stations = ['RS106', 'RS205', 'RS208', 'RS210', 'RS305', 'RS306', 'RS307', 'RS310', 'RS406', 'RS407', 'RS409', 'RS503', 'RS508', 'RS509', 'DE601', 'DE602', 'DE603', 'DE604', 'DE605', 'FR606', 'SE607', 'UK608', 'ST001']

pdfs = []
merged = PdfFileMerger()
count = 0

# the CASA and AIPS delays had a different number of data points so this is to normalise the x-axis

time_axis119 = range(119)
time_axis89 = []

for i in range(89):
    time_axis89.append(i * 1.337)


### 1.4 Make the plot

for s in stations:

    ''' CASA --------------------------------------------------------------------------------------------------- '''

    casa_data_time = []
    casa_data_pol1 = []
    casa_data_pol2 = []

    for j in range(len(x)):
        if int(x[j]) == count:
            casa_data_time.append(w[j])
            casa_data_pol1.append(y[j])
            casa_data_pol2.append(z[j])

    count = count + 1

    for i in range(len(casa_data_pol1)):
        if casa_data_pol1[i] > 350 or casa_data_pol1[i] < -350:
            casa_data_pol1[i] = casa_data_pol1[i - 1]
            
    ''' AIPS --------------------------------------------------------------------------------------------------- '''

    station_time = []
    station_pol1 = []
    station_pol2 = []
    station = s

    for i in range(len(time)):
        if frequency[i] == 129685974.12 and antenna[i] == station:
            station_time.append(time[i])
            station_pol1.append(pol1[i] * 1e9)

    for i in range(len(station_pol1)):
        if station_pol1[i] > 350 or station_pol1[i] < -200:
            station_pol1[i] = station_pol1[i - 1]
    
    ''' Plot --------------------------------------------------------------------------------------------------- '''

    plt.figure(figsize = (10, 8))
    plt.title('Polarisation 1 for ' + station)
    plt.xlabel('Time')
    plt.ylabel('Delay (ns)')

    plt.plot(time_axis89, casa_data_pol1, color = 'red', label = 'CASA')    
    plt.plot(time_axis119, station_pol1, label = 'AIPS')
    
    plt.legend()
    plt.savefig('station-' + s + '.pdf', bbox_inches = 'tight', format = 'pdf')
    pdfs.append('station-' + s + '.pdf')
    plt.clf()


### 1.5 Sort out the PDFs

for pdf in pdfs:
    merged.append(pdf)

merged.write('delays.pdf')

for pdf in pdfs:
    os.remove(pdf)

# and you end with one PDF final called delays.pdf
