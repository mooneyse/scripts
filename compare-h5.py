#!/usr/bin/env python

# default option isn't working
import matplotlib as mpl
mpl.use('Agg')

import os
import numpy as np
import matplotlib.pyplot as plt
import losoto.h5parm as lh5

def get_data(h5_file, object):
    solsetnames = object.getSolsetNames()
    soltabnames = object.getSolset(solsetnames[0]).getSoltabNames()
    # print('solsets:', solsetnames)
    # print(solsetnames[0], 'soltabs:', soltabnames)

    clock = object.getSolset(solsetnames[0]).getSoltab('clock000')
    polalign = object.getSolset(solsetnames[0]).getSoltab('polalign')
    bandpass = object.getSolset(solsetnames[0]).getSoltab('bandpass')
    rotationmeasure = object.getSolset(solsetnames[0]).getSoltab(
        'rotationmeasure000')

    return clock, polalign, bandpass, rotationmeasure

def plotting(name, soltab, soltab_lb, ant, ant_lb, time, time_lb):
    # international stations are between core and remote station so the indices
    # will not match
    ant_name = ant[i]
    j = list(ant_lb).index(ant_name)
    ant_name_lb = ant_lb[j]

    if name == 'clock': # time on different axis for clock and rotation measure
    # for time we use CS001HBA as the reference station
        val = (soltab.val[:, i] - np.mean(soltab.val[:, 0])) * 1e9
        val_lb = (soltab_lb.val[:, j] - np.mean(clock_lb.val[:, 0])) * 1e9
    else:
        val = (soltab.val[i, :] * 1e9)
        val_lb = (soltab_lb.val[j, :] * 1e9)

    plt.figure(figsize = (16, 8))
    plt.plot(time, val, 'b-', label = ant_name)
    plt.plot(time_lb, val_lb, 'r-', label = ant_name_lb + ' LB')
    plt.xlim(min(time), max(time))

    no_lb_average = int(np.round(np.mean(val), 0))
    with_lb_average = int(np.round(np.mean(val_lb), 0))
    # ratio = np.round(abs(with_lb_average) / abs(no_lb_average), 2)
    difference = int(np.round(np.mean(val) - np.mean(val_lb), 0))

    title = (name + ' solutions  ||  no-LB average: ' + str(no_lb_average) +
        '  ||  with-LB average: ' + str(with_lb_average) + '  ||  difference: '
        + str(difference))
    plt.title(title)
    plt.xlabel('Time (timestep)')
    plt.ylabel(name)
    plt.legend()
    plt.tight_layout()

    directory = '/home/sean/Downloads/images/compare-h5/' + name
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(directory + '/' + ant_name + '.png')
    plt.close()

# get the data
cal_h5 = '/home/sean/Downloads/other/cal.h5'
cal_h5_lb = '/home/sean/Downloads/other/cal-lb.h5'
h = lh5.h5parm(cal_h5)
h_lb = lh5.h5parm(cal_h5_lb)

clock, polalign, bandpass, rotationmeasure = get_data(h5_file=cal_h5, object=h)
clock_lb, polalign_lb, bandpass_lb, rotationmeasure_lb = get_data(
    h5_file=cal_h5_lb, object=h_lb)

# plot the clocks
# print(clock.getAxesNames())
# print(clock.getAxisLen('time'))
for i in range(clock.getAxisLen('ant')):
    plotting(
        name='clock',
        soltab=clock,
        soltab_lb=clock_lb,
        ant=clock.getAxisValues('ant'),
        ant_lb=clock_lb.getAxisValues('ant'),
        time=clock.getAxisValues('time'),
        time_lb=clock_lb.getAxisValues('time'))

# plot the rotation measure
for i in range(rotationmeasure.getAxisLen('ant')):
    plotting(
        name='rotationmeasure',
        soltab=rotationmeasure,
        soltab_lb=rotationmeasure_lb,
        ant=rotationmeasure.getAxisValues('ant'),
        ant_lb=rotationmeasure.getAxisValues('ant'),
        time=rotationmeasure.getAxisValues('time'),
        time_lb=rotationmeasure.getAxisValues('time'))

# close files
h.close()
h_lb.close()
