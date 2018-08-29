import losoto.h5parm as lh5
import numpy as np

def h5_values(my_h5parm, station):

    lo = lh5.h5parm(my_h5parm, readonly = False)
    phase = lo.getSolset('sol000').getSoltab('phase000')
    values = phase.val[0, 0, station, 0, :] # (pol, dir, ant, freq, time)

    lo.close()

    return values

values = h5_values('../other/test.h5', 0)

print(values)
