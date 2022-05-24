import sys
from pylab import *

from parse.parse_fitfile import parse_fitfile
from calc.calc_power import calc_power_data

def power_rmsq(data_pow, comp_pow, include_coasting = False):
    dsq = 0.
    np = 0
    for it, dat in enumerate(data_pow):
        if dat > 0 or include_coasting:
            dsq += (comp_pow[it] - dat)**2
            np += 1
    return sqrt(dsq/np)

# setup dict of relevant entries
entry_dict = {'speed' : [], 'power' : [], 'distance' : [], 'position_lat' : [], 'position_long' : [], 'altitude' : []}

# Parse the FIT file
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

phys_var_0 = {
    'mass'     : 73+9,
    'crr'      : 0.004,
    'cda'      : 0.215,
    'rho'      : 1.225,
    'g'        : 9.81,
    'loss'     : 0.025,
    'wind_v'   : 1.,
    'wind_dir' : -70. 
}

cda_min = 0.195
cda_max = 0.235
cda_delta = 0.0025
n_cda = int((cda_max - cda_min)/cda_delta) + 1

wind_v_min = 0.
wind_v_max = 5.
wind_v_delta = 0.5
n_wind_v = int((wind_v_max - wind_v_min)/wind_v_delta) + 1

wind_dir_min = 0.
wind_dir_max = 350.
wind_dir_delta = 25.
n_wind_dir = int((wind_dir_max - wind_dir_min)/wind_dir_delta) + 1

min_rmsq = -1.
cda_best = -1
wind_v_best = -1.
wind_dir_best = -1.
comp_pow_best = []

for cda in linspace(cda_min, cda_max, n_cda, True):
    for wind_v in linspace(wind_v_min, wind_v_max, n_wind_v, True):
        for wind_dir in linspace(wind_dir_min, wind_dir_max, n_wind_dir, True):
            print(cda, wind_v, wind_dir)
            phys_var = phys_var_0
            phys_var['cda'] = cda
            phys_var['wind_v'] = wind_v
            phys_var['wind_dir'] = wind_dir

            comp_pow = calc_power_data(data, phys_var, True, 0)
            rmsq = power_rmsq(data['power'], comp_pow)

            if rmsq < min_rmsq or min_rmsq < 0:
                cda_best = cda
                wind_v_best = wind_v
                wind_dir_best = wind_dir
                comp_pow_best = comp_pow
                min_rmsq = rmsq

print('Optimization Results:')
print('cda:      ', cda_best)
print('wind_v:   ', wind_v_best)
print('wind_dir: ', wind_dir_best)
print()
print('Min RMSQ: ', min_rmsq)

comp_pow = comp_pow_best
avg_pow = mean(comp_pow)

#if verbosity > 0:
#    for it, dat in enumerate(data['power']):
#        print(dat, comp_pow[it])

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

