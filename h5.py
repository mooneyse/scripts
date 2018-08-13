import os
import numpy as np
import matplotlib.pyplot as plt
from losoto.h5parm import h5parm

# get the data -----------------------------------------------------------------------------------------------------

name = '/home/sean/test.h5'
h5 = h5parm(name, readonly = True)
tec_data = h5.getSoltab('sol000', 'tec000')
clock_data = h5.getSoltab('sol000', 'clock000')

# set the options --------------------------------------------------------------------------------------------------

clip = False
both_polarisations = False
scale = 0.75

if clip:
    print('Clipping is enabled with a scaling factor of ' + str(scale) + '.')
else:
    print('Clipping is disabled.')

polarisation_range = 2 if both_polarisations else 1

# set up the plot --------------------------------------------------------------------------------------------------

station_list = []

for station in range(len(clock_data.ant[:])): # 0 to 67 inclusive
    station_list.append(str(clock_data.ant[station]).split("'")[1])

    plt.figure(figsize = (10, 8))
    plt.xlabel('Time')
    plt.ylabel('Clock (ns)')
    plt.title('Station ' + str(station_list[station]))

    for polarisation in range(polarisation_range):

        clocks = []
        for clock in range(843):
            clocks.append(clock_data.val[clock, station, polarisation] * 1e9) # change to nanoseconds

# clip the outliers ------------------------------------------------------------------------------------------------

        if clip:
            scale = 0.75

            print()
            print('These data for polarisation ' + str(polarisation) + ' have been clipped:')
            for i in range(len(clocks)):
                if clocks[i] > clocks[i - 1] * (1 + scale) or clocks[i] < clocks[i - 1] / (1 - scale):
                    print('- ' + str(clocks[i]) + ' (point ' + str(i) + ') has been changed to ' + str(clocks[i - 1]) + ' (point ' + str(i - 1) + ')')
                    clocks[i] = clocks[i - 1]

# make the plot ----------------------------------------------------------------------------------------------------

        plt.xlim(0, len(clocks))
        colors = 'blue' if polarisation == 0 else 'red'
        labels = 'Polarisation ' + str(polarisation + 1)
        plt.plot(clocks, lw = 0.5, color = colors, label = labels)
        if both_polarisations:
            plt.legend()

    plt.show()
