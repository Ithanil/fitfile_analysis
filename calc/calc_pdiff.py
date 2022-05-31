from pylab import *

def calc_pdiff(data_pow, data_v, comp_pow, no_filter = False):
    dsq = 0.
    np = 0
    for it, dat in enumerate(data_pow):
        if it > 0:
            if (dat > 0 and data_v[it] > 2. and abs(data_v[it] - data_v[it-1]) < 0.5) or no_filter:
                dsq += (comp_pow[it] - dat)**2
                np += 1
    return dsq, np