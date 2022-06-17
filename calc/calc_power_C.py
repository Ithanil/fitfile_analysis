from ctypes import *
from numpy import empty, double

class PhysVar(Structure):
    _fields_ = [("mass", c_double),
                ("rot_mass", c_double),
                ("crr", c_double),
                ("cda", c_double),
                ("rho", c_double),
                ("g", c_double),
                ("loss", c_double),
                ("wind_v", c_double),
                ("wind_dir", c_double)]

def calc_power_data_C(lib, data, phys_var, use_zero_slope = False, calc_neg_watts = True):
    # prepare c function
    calc_power_data_cfun = lib.calc_power_data
    calc_power_data_cfun.restype = c_void_p

    # prepare arguments
    ndata = len(data['speed'])
    comp_pow = empty(ndata, dtype=double)
    phys_var_struct = PhysVar(phys_var['mass'], phys_var['rot_mass'], phys_var['crr'], phys_var['cda'], phys_var['rho'],
                              phys_var['g'], phys_var['loss'], phys_var['wind_v'], phys_var['wind_dir'])

    # call function
    calc_power_data_cfun(c_int(ndata),
                    c_void_p(comp_pow.ctypes.data),
                    c_void_p(data['speed'].ctypes.data),
                    c_void_p(data['position_lat'].ctypes.data),
                    c_void_p(data['position_long'].ctypes.data),
                    c_void_p(data['slope'].ctypes.data),
                    c_void_p(data['seconds'].ctypes.data),
                    phys_var_struct,
                    c_int(use_zero_slope),
                    c_int(calc_neg_watts))

    return comp_pow
