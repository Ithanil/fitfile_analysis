import sys
from pylab import *

from parse.parse_fitfile import parse_fitfile
from calc.calc_power import calc_power_data

verbosity = 0
calc_neg_watts = False # if true, don't treat computed negative watt values as 0

# setup dict of relevant entries
entry_dict = {'speed' : [], 'power' : [], 'distance' : [], 'position_lat' : [], 'position_long' : [], 'altitude' : []}

# Parse the FIT file
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

phys_var = {
    'mass'       : 75+9,
    'im_wheels'  : 0.5,
    'circ_wheels': 2.105,
    'crr'        : 0.004,
    'cda'        : 0.22,
    'rho'        : 1.225,
    'g'          : 9.81,
    'loss'       : 0.03,
    'wind_v'     : 0.,
    'wind_dir'   : -70. 
}
comp_pow = calc_power_data(data, phys_var, calc_neg_watts, verbosity)
avg_pow = mean(comp_pow)

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

