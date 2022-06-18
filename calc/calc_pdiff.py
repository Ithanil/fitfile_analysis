from pylab import *

def calc_pdiff(data_pow, data_v, comp_pow, no_filter = False):
    cost = 0.
    np = 0
    for it, dat in enumerate(data_pow):
        if it > 0:
            if (dat > 0 and data_v[it] > 20. and abs(data_v[it] - data_v[it-1]) < 2.) or no_filter:
                pdiff = (comp_pow[it] - dat)
                cost += pdiff + pdiff**2
                np += 1
    return abs(cost), np
