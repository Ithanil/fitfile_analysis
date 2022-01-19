import sys
from parse.parse_fitfile import parse_fitfile
from pylab import *

# setup dict of relevant entries
entry_dict = {'speed' : [], 'power' : [], 'distance' : [], 'position_lat' : [], 'position_long' : [], 'altitude' : []}

# Parse the FIT file
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

phys_var = {
    'mass' : 73+9,
    'crr'  : 0.0035,
    'cda'  : 0.23,
    'rho'  : 1.225,
    'g'    : 9.81,
    'loss' : 0.03
}

def power_calc(v, slope, phys_var):
    slope_rad = arctan(slope)/180*pi
    F_g = phys_var['mass'] * phys_var['g'] * sin(slope_rad)
    F_r = phys_var['mass'] * phys_var['g'] * cos(slope_rad) * phys_var['crr']
    F_a = 0.5 * phys_var['cda'] * phys_var['rho'] * v*v
    #print(F_g, F_r, F_a)

    return (F_g + F_r + F_a) * v / (1 - phys_var['loss'])


comp_pow = []
avg_pow = 0
for it in range(len(data['speed'])):
    pow = power_calc(data['speed'][it]/3.6, data['slope'][it], phys_var)
    comp_pow.append(pow)
    avg_pow += pow
comp_pow = array(comp_pow)
avg_pow /= len(comp_pow)

print(comp_pow)
print(data['power'])
print('Calculated average power: ', avg_pow)
print('Measured average power: ', mean(data['power']))