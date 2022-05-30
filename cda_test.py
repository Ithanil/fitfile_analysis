import sys
from pylab import *
from meteostat import Point, Hourly
from datetime import datetime

from parse.parse_fitfile import parse_fitfile
from calc.calc_power import calc_power_data

def calc_rho_air(temp, pres, rhum):
# Units: temp in °C, pres in hPa, rhum in %
    t_K = temp + 273.15
    p_Pa = pres * 100.
    rh = rhum / 100.

    psat = 610.78 * exp(17.27*temp / (temp + 237.3))
    pv = rh * psat
    pd = p_Pa - pv

    return pd/(287.058*t_K) + pv/(461.495*t_K)

verbosity = 0
calc_neg_watts = False # if true, don't treat computed negative watt values as 0

# setup dict of relevant entries
entry_dict = {'speed' : [], 'power' : [], 'distance' : [], 'position_lat' : [], 'position_long' : [], 'altitude' : []}

# Parse the FIT file
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

# Set time period
tstart = data['timestamp'][0]
tstart = datetime(tstart.year, tstart.month, tstart.day, tstart.hour)

# Create Point
location = Point(data['position_lat'][0], data['position_long'][0])#, data['altitude'][0])

# Get hourly data
weather_data = Hourly(location, tstart, tstart)
weather_data = weather_data.fetch()

print(weather_data)
print(weather_data.temp, weather_data.rhum, weather_data.pres)
rho_calc = calc_rho_air(weather_data.temp[0], weather_data.pres[0], weather_data.rhum[0])
print('rho calc: ', rho_calc)

phys_var = {
    'mass'       : 75+9,
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

