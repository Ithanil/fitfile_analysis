import sys
from parse.parse_fitfile import parse_fitfile
from pylab import *

verbosity = 0
calc_neg_watts = 0 # don't treat computed negative watt values as 0

# setup dict of relevant entries
entry_dict = {'speed' : [], 'power' : [], 'distance' : [], 'position_lat' : [], 'position_long' : [], 'altitude' : []}

# Parse the FIT file
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

phys_var = {
    'mass' : 73+9,
    'crr'  : 0.004,
    'cda'  : 0.22,
    'rho'  : 1.225,
    'g'    : 9.81,
    'loss' : 0.025
}

def power_calc(v_new, v_old, slope, phys_var):
    slope_rad = arctan(slope)
    v = 0.5*(v_new + v_old)

    F_g = phys_var['mass'] * phys_var['g'] * sin(slope_rad)
    F_r = phys_var['mass'] * phys_var['g'] * cos(slope_rad) * phys_var['crr']
    F_w = 0.5 * phys_var['cda'] * phys_var['rho'] * v*v
    
    pow_base = (F_g + F_r + F_w) * v
    pow_acc = 0.5*phys_var['mass']*(v_new**2 - v_old**2)

    if verbosity > 1:
        print(F_g, F_r, F_w)
        print(v_new, v_old, pow_base, pow_acc)

    if pow_base + pow_acc > 0 or calc_neg_watts:
        return (pow_base + pow_acc) / (1 - phys_var['loss'])
    else:
        return 0.


comp_pow = []
avg_pow = 0
v_old = 0.
for it in range(len(data['speed'])):
    v_new = data['speed'][it]/3.6
    pow = power_calc(v_new, v_old, data['slope'][it], phys_var)
#    print(data['slope'][it]*100., arctan(data['slope'][it])*180./pi)
    comp_pow.append(pow)
    avg_pow += pow
    v_old = v_new
comp_pow = array(comp_pow)
avg_pow /= len(comp_pow)

if verbosity > 0:
    for it, dat in enumerate(data['power']):
        print(dat, comp_pow[it])

print('Calculated average power: ', avg_pow)
print('Measured average power: ', mean(data['power']))

win_len = 60
data_smooth = []
comp_smooth = []
cont = 0
dat_movavg = 0.
comp_movavg = 0.
for it, dat in enumerate(data['power']):
    dat_movavg += dat
    comp_movavg += comp_pow[it]
    cont += 1

    if cont == win_len:
        data_smooth.append(dat_movavg / win_len)
        comp_smooth.append(comp_movavg / win_len)
        cont = 0
        dat_movavg = 0.
        comp_movavg = 0.

figure()
plot(data['power'], 'x')
plot(comp_pow, '+')

figure()
plot(data_smooth)
plot(comp_smooth)

show()

