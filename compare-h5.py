#!/usr/bin/env python
import matplotlib as mpl
mpl.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import losoto.h5parm as lh5

# get the data
cal_h5 = '/home/sean/Downloads/other/cal.h5'
cal_h5_lb = '/home/sean/Downloads/other/cal-lb.h5'

def get_data(h5_file):
    h = lh5.h5parm(h5_file)
    solsetnames = h.getSolsetNames()
    soltabnames = h.getSolset(solsetnames[0]).getSoltabNames()
    # print('solsets:', solsetnames)
    # print(solsetnames[0], 'soltabs:', soltabnames)

    clock = h.getSolset(solsetnames[0]).getSoltab('clock000')
    polalign = h.getSolset(solsetnames[0]).getSoltab('polalign')
    bandpass = h.getSolset(solsetnames[0]).getSoltab('bandpass')
    rotationmeasure = h.getSolset(solsetnames[0]).getSoltab('rotationmeasure000')

    # h.close()
    return clock, polalign, bandpass, rotationmeasure

clock, polalign, bandpass, rotationmeasure = get_data(cal_h5)
clock_lb, polalign_lb, bandpass_lb, rotationmeasure_lb = get_data(cal_h5_lb)

# plot the clocks
# print(clock.getAxesNames())
clock_time = clock.getAxisValues('time')
clock_ant = clock.getAxisValues('ant')
# print(clock.getAxisLen('time'))

clock_time_lb = clock_lb.getAxisValues('time')
clock_ant_lb = clock_lb.getAxisValues('ant')

for i in range(clock.getAxisLen('ant')):
    ant_name = clock_ant[i]

    clock_val = (clock.val[:, i] - np.mean(clock.val[:, 0])) * 1e9 # subtract average CS001 clock value
    clock_val_lb = (clock_lb.val[:, i] - np.mean(clock_lb.val[:, 0])) * 1e9 # subtract average CS001 clock value
    plt.figure(figsize = (16, 8))

    plt.plot(clock_time, clock_val, 'b-', label = ant_name)
    plt.plot(clock_time_lb, clock_val_lb, 'r-', label = ant_name + ' LB')

    plt.xlim(min(clock_time), max(clock_time))
    no_lb_average = np.round(np.mean(clock_val), 2)
    with_lb_average = np.round(np.mean(clock_val_lb), 2)
    ratio = np.round(abs(with_lb_average) / abs(no_lb_average), 2)
    difference = np.round(np.mean(clock_val) - np.mean(clock_val_lb), 2)
    title = 'Clock solutions  ||  no-LB average: ' + str(no_lb_average) + '  ||  with-LB average: ' + str(with_lb_average) + '  ||  difference: ' + str(difference)
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('Nanoseconds')
    plt.legend()
    plt.tight_layout()
    plt.savefig('/home/sean/Downloads/images/compare-h5/refCS001/refCS001-' + ant_name + '.png')
    plt.close()
