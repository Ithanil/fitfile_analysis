import sys
from pylab import *
from ctypes import cdll

from parse.parse_fitfile import parse_fitfile, extract_data_segment
from calc.calc_power_C import calc_power_data_C
from parse.get_weather_data import get_weather_data
from calc.calc_rho import calc_rho_humid

def pdiff_msq(data_pow, comp_pow, no_filter = False):
    dsq = 0.
    np = 0
    for it, dat in enumerate(data_pow):
        if (dat > 0 and data_v[it] > 2. and abs(data_v[it] - data_v[it-1]) < 0.5) or no_filter:
            dsq += (comp_pow[it] - dat)**2
            np += 1
    return dsq/np

def pdiff_sq_np(data_pow, data_v, comp_pow, no_filter = False):
    dsq = 0.
    np = 0
    for it, dat in enumerate(data_pow):
        if it > 0:
            if (dat > 0 and data_v[it] > 2. and abs(data_v[it] - data_v[it-1]) < 0.5) or no_filter:
                dsq += (comp_pow[it] - dat)**2
                np += 1
    return dsq, np

# load C library
lib = cdll.LoadLibrary("calc/calc_power_C.o")

phys_var_0 = {
    'mass'        : 73.5+9,
    'rot_mass'    : 0.5 * 4.*pi**2 / 2.105**2,
    'crr'         : 0.004,
    'cda'         : 0.22,
    'rho'         : 1.225,
    'g'           : 9.81,
    'loss'        : 0.03,
    'wind_v'      : 0.,
    'wind_dir'    : 0. 
}

# to correct for known errors:
power_factor = 1.0
speed_factor = 1.0

# to pick certain segments
#segment_timestamps = [[21, 234], [355, 702], [731, 977], [1058, 1401]]
segment_timestamps = [[]]

# parameter search ranges
cda_min = 0.21
cda_max = 0.23
cda_delta = 0.001
n_cda = int((cda_max - cda_min)/cda_delta) + 1

crr_min = 0.003
crr_max = 0.005
crr_delta = 0.00025
n_crr = int((crr_max - crr_min)/crr_delta) + 1

wind_v_min = 0.0
wind_v_max = 5.0
wind_v_delta = 0.277777777
n_wind_v = int((wind_v_max - wind_v_min)/wind_v_delta) + 1

wind_dir_min = 0.
wind_dir_max = 348.75
wind_dir_delta = 11.25
n_wind_dir = int((wind_dir_max - wind_dir_min)/wind_dir_delta) + 1


# setup dict of relevant entries and parse the FIT file
entry_dict = {'speed' : [], 'power' : [], 'distance' : [], 'position_lat' : [], 'position_long' : [], 'altitude' : []}
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)
for it, pow in enumerate(data['power']):
    data['power'][it] = power_factor*pow
for it, spd in enumerate(data['speed']):
    data['speed'][it] = speed_factor*spd


# get weather data and compute rho
weather_data = get_weather_data(data)
rho_calc = calc_rho_humid(weather_data.temp[0], weather_data.pres[0], weather_data.rhum[0])
print('Weather Data:')
print(weather_data)
print('Computed Air Rho: ', rho_calc)
phys_var_0['rho'] = rho_calc

min_msq = -1.
phys_var_best = phys_var_0
for cda in linspace(cda_min, cda_max, n_cda, True):
    for crr in linspace(crr_min, crr_max, n_crr, True):
        for wind_v in linspace(wind_v_min, wind_v_max, n_wind_v, True):
            for wind_dir in linspace(wind_dir_min, wind_dir_max, n_wind_dir, True):
                if wind_v == 0 and wind_dir > 0:
                    continue # no sense to check different directions for 0 wind
                print(cda, crr, wind_v, wind_dir)
                phys_var = phys_var_0.copy()
                phys_var['cda'] = cda
                phys_var['crr'] = crr
                phys_var['wind_v'] = wind_v
                phys_var['wind_dir'] = wind_dir

                msq = 0.
                np = 0
                for seg in segment_timestamps:
                    if seg != []:
                        data_seg = extract_data_segment(data, seg[0], seg[1])
                    else:
                        if len(segment_timestamps) > 1:
                            print('Error: More than one segment in list, but one was empty!')
                        data_seg = data

                    comp_pow = calc_power_data_C(lib, data_seg, phys_var, True)
                    sq, n = pdiff_sq_np(data_seg['power'], data_seg['speed'], comp_pow) 
                    msq += sq
                    np += n
                msq /= np

                if msq < min_msq or min_msq < 0:
                    phys_var_best = phys_var.copy()
                    min_msq = msq

print('Optimization Results:')
print('cda:      ', phys_var_best['cda'])
print('crr:      ', phys_var_best['crr'])
print('wind_v:   ', phys_var_best['wind_v'])
print('wind_dir: ', phys_var_best['wind_dir'])
print()
print('Min RMSQ: ', sqrt(min_msq))

comp_pow = calc_power_data_C(lib, data, phys_var_best, True)
avg_pow = mean(comp_pow)

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
