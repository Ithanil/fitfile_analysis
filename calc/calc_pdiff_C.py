from ctypes import *
from numpy import empty, double

def calc_pdiff_C(lib, data_pow, data_v, comp_pow, no_filter = False):
    # prepare c function
    calc_pdiff_sq_np_cfun = lib.calc_pdiff
    calc_pdiff_sq_np_cfun.restype = c_int

    # prepare arguments
    ndata = len(data_pow)
    cost = c_double()

    # call function
    np = calc_pdiff_sq_np_cfun(c_int(ndata), pointer(cost),
                     c_void_p(data_pow.ctypes.data),
                     c_void_p(data_v.ctypes.data),
                     c_void_p(comp_pow.ctypes.data),
                     c_int(no_filter))

    return double(cost), np
