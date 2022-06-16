import sys

from parse.parse_fitfile import parse_fitfile
from pylab import *

def calc_direction(Alat, Along, Blat, Blong):
    Alat_rad = Alat/180.*pi
    Along_rad = Along/180.*pi
    Blat_rad = Blat/180.*pi
    Blong_rad = Blong/180.*pi

    deltaL = Blong_rad - Along_rad
    X = cos(Blat_rad)*sin(deltaL)
    Y = cos(Alat_rad)*sin(Blat_rad) - sin(Alat_rad)*cos(Blat_rad)*cos(deltaL)

    return arctan2(X, Y)/pi*180. + 180.

def calc_power(v_new, v_old, tdiff, dir, slope, phys_var, verbosity = 0):
    slope_rad = arctan(slope)
    v = 0.5*(v_new + v_old)
    v_wind = v - phys_var['wind_v'] * cos((dir - phys_var['wind_dir'])/180.*pi)

    F_g = phys_var['mass'] * phys_var['g'] * sin(slope_rad)
    F_r = phys_var['mass'] * phys_var['g'] * abs(cos(slope_rad)) * phys_var['crr']
    F_w = 0.5 * phys_var['cda'] * phys_var['rho'] * v_wind*v_wind
    pow_base = (F_g + F_r + F_w) * v

    diff_ekin = 0.5*phys_var['mass']*(v_new**2 - v_old**2)
    diff_erot = 0.5*phys_var['rot_mass']*(v_new**2 - v_old**2)
    pow_acc = (diff_ekin + diff_erot) / tdiff

    if verbosity > 1:
        print('Forces g/r/w: ', F_g, F_r, F_w)
        print('Powers g/r/w/a: ', F_g*v, F_r*v, F_w*v, pow_acc)
        print('Ekin_new: ', 0.5*phys_var['mass']*v_new**2, ' Erot_new: ', 0.5*phys_var['rot_mass']*v_new**2)
        print('Diff Ekin, Diff Erot, Power: ', diff_ekin, diff_erot, pow_base+pow_acc)

    return (pow_base + pow_acc) / (1 - phys_var['loss'])

def calc_power_data(data, phys_var, calc_neg_watts = True, verbosity = 0):
#data needs to contain the following entries:
#'speed', 'power', 'distance', 'position_lat', 'position_long', 'altitude'
#
#Physical parameter dictionary example:
#phys_var = {
#    'mass'     : 73+9,
#    'crr'      : 0.004,
#    'cda'      : 0.215,
#    'rho'      : 1.225,
#    'g'        : 9.81,
#    'loss'     : 0.025,
#    'wind_v'   : 1.,
#    'wind_dir' : -70.
#}
    comp_pow = []
    v_old = data['speed'][0]/3.6
    ndata = len(data['speed'])
    for it in range(ndata):
        v_new = data['speed'][it]/3.6

        # compute time difference
        if it > 0:
            tdiff = data['seconds'][it] - data['seconds'][it-1]
        else:
            tdiff = 1.

        # compute smoothed direction
        if it == ndata - 1: # last step
            dir = calc_direction(data['position_lat'][it-1], data['position_long'][it-1], data['position_lat'][it], data['position_long'][it])
        elif it > 0: # regular step
            dir = calc_direction(data['position_lat'][it-1], data['position_long'][it-1], data['position_lat'][it+1], data['position_long'][it+1])
        else: # first step: assume perfect cross wind
            dir = phys_var['wind_dir'] + 90.

        # compute power
        pow = calc_power(v_new, v_old, tdiff, dir, data['slope'][it], phys_var, verbosity)
        if pow > 0 or calc_neg_watts: # option to clamp power to positive values
            comp_pow.append(pow)
        else:
            comp_pow.append(0.)
        v_old = v_new

    return array(comp_pow)

