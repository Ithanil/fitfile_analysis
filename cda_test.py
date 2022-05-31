import sys
from pylab import *

from parse.parse_fitfile import parse_fitfile
from calc.calc_power import calc_power_data
from parse.get_weather_data import get_weather_data
from calc.calc_rho import calc_rho_humid

verbosity = 0
calc_neg_watts = True # if true, don't treat computed negative watt values as 0

# setup dict of relevant entries
entry_dict = {'speed' : [], 'power' : [], 'distance' : [], 'position_lat' : [], 'position_long' : [], 'altitude' : []}

# Parse the FIT file
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

# get weather
weather_data = get_weather_data(data)
rho_calc = calc_rho_humid(weather_data.temp[0], weather_data.pres[0], weather_data.rhum[0])
print('Weather Data:')
print(weather_data)
print('Computed Air Rho: ', rho_calc)

phys_var = {
    'mass'       : 73.5+9,
    'rot_mass'   : 0.5 * 4.*pi**2 / 2.105**2,
    'crr'        : 0.004,
    'cda'        : 0.22,
    'rho'        : rho_calc,
    'g'          : 9.81,
    'loss'       : 0.03,
    'wind_v'     : 0.,
    'wind_dir'   : 0. 
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
it = 0
while it < len(comp_pow) - win_len + 1:
    win_dat = data['power'][it : it + win_len]
    win_comp = comp_pow[it : it + win_len]

    avg_dat = mean(win_dat)
    avg_comp = mean(win_comp)

    data_smooth.append(avg_dat)
    comp_smooth.append(avg_comp)

    it += 1

figure()
plot(data['power'], 'x')
plot(comp_pow, '+')

figure()
plot(data_smooth)
plot(comp_smooth)

show()

