import sys
from pylab import *
from ctypes import cdll
from datetime import datetime

from parse.parse_fitfile import parse_fitfile, extract_data_segment_secs, extract_data_segment_time
from calc.calc_power_C import calc_power_data_C
#from calc.calc_power import calc_power_data
from calc.calc_pdiff_C import calc_pdiff_C
from parse.get_weather_data import get_weather_data
from calc.calc_rho import calc_rho_humid

# load C libraries
lib_power = cdll.LoadLibrary("calc/calc_power.o")
lib_pdiff = cdll.LoadLibrary("calc/calc_pdiff.o")

phys_var_0 = {
    'mass'        : 73+9,
    'rot_mass'    : 0.15 * 4.*pi**2 / 2.105**2,
    'crr'         : 0.0035,
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
use_zero_slope = False

# to pick certain segments

# Auringen 20201
#segment_timestamps = [[21, 234], [355, 702], [731, 977], [1058, 1401]]

# Aero Test 05/22
#segment_timestamps = [[datetime(2022, 5, 26, 15, 52, 44), datetime(2022, 5, 26, 15, 56, 2)], [datetime(2022, 5, 26, 15, 58, 51), datetime(2022, 5, 26, 16, 1, 52)],
#                      [datetime(2022, 5, 26, 16, 2, 42), datetime(2022, 5, 26, 16, 5, 49)], [datetime(2022, 5, 26, 16, 8, 51), datetime(2022, 5, 26, 16, 11, 39)]]
#segment_timestamps = [[datetime(2022, 5, 26, 16, 12, 34), datetime(2022, 5, 26, 16, 15, 38)], [datetime(2022, 5, 26, 16, 16, 8), datetime(2022, 5, 26, 16, 18, 53)],
#                      [datetime(2022, 5, 26, 16, 19, 50), datetime(2022, 5, 26, 16, 23, 11)], [datetime(2022, 5, 26, 16, 23, 46), datetime(2022, 5, 26, 16, 26, 33)]]

# Aero Test 06/22
#segment_timestamps = [[datetime(2022, 6, 15, 17, 32, 54), datetime(2022, 6, 15, 17, 34, 48)], [datetime(2022, 6, 15, 17, 36, 7), datetime(2022, 6, 15, 17, 37, 53)],
#                      [datetime(2022, 6, 15, 17, 50, 3), datetime(2022, 6, 15, 17, 51, 55)], [datetime(2022, 6, 15, 17, 53, 15), datetime(2022, 6, 15, 17, 55, 1)],
#                      [datetime(2022, 6, 15, 18, 7, 19), datetime(2022, 6, 15, 18, 9, 27)], [datetime(2022, 6, 15, 18, 9, 55), datetime(2022, 6, 15, 18, 11, 51)]]

segment_timestamps = [[datetime(2022, 6, 15, 17, 32, 54), datetime(2022, 6, 15, 17, 34, 48)], [datetime(2022, 6, 15, 17, 36, 7), datetime(2022, 6, 15, 17, 37, 53)],
                      [datetime(2022, 6, 15, 17, 50, 3), datetime(2022, 6, 15, 17, 51, 55)], [datetime(2022, 6, 15, 17, 53, 15), datetime(2022, 6, 15, 17, 55, 1)]]
#segment_timestamps = [[datetime(2022, 6, 15, 17, 39, 18), datetime(2022, 6, 15, 17, 41, 4)], [datetime(2022, 6, 15, 17, 42, 25), datetime(2022, 6, 15, 17, 44, 12)],
#                      [datetime(2022, 6, 15, 17, 56, 33), datetime(2022, 6, 15, 17, 58, 19)], [datetime(2022, 6, 15, 17, 59, 45), datetime(2022, 6, 15, 18, 1, 29)]]

#segment_timestamps = [[]]

# parameter search ranges
cda_min = 0.21
cda_max = 0.24
cda_delta = 0.001
n_cda = int((cda_max - cda_min)/cda_delta) + 1

crr_min = 0.003
crr_max = 0.003
crr_delta = 0.00025
n_crr = int((crr_max - crr_min)/crr_delta) + 1

wind_v_min = 0.0
wind_v_max = 5.55555556
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
phys_var_0['rho'] = rho_calc

# prepare data segments
data_segments = []
for seg in segment_timestamps:
    if seg != []:
        data_segments.append(extract_data_segment_time(data, seg[0], seg[1]))
    else:
        if len(segment_timestamps) > 1:
            print('Error: More than one segment in list, but one was empty!')
        data_segments.append(data)

min_msq = -1.
phys_var_best = phys_var_0
for cda in linspace(cda_min, cda_max, n_cda, True):
    for crr in linspace(crr_min, crr_max, n_crr, True):
        for wind_v in linspace(wind_v_min, wind_v_max, n_wind_v, True):
            for wind_dir in linspace(wind_dir_min, wind_dir_max, n_wind_dir, True):
                if wind_v == 0 and wind_dir > 0:
                    continue # no sense to check different directions for 0 wind
                phys_var = phys_var_0.copy()
                phys_var['cda'] = cda
                phys_var['crr'] = crr
                phys_var['wind_v'] = wind_v
                phys_var['wind_dir'] = wind_dir

                msq = 0.
                np = 0
                for data_seg in data_segments:
                    comp_pow = calc_power_data_C(lib_power, data_seg, phys_var, use_zero_slope, True)
                    sq, n = calc_pdiff_C(lib_pdiff, data_seg['power'], data_seg['speed'], comp_pow)
                    msq += sq
                    np += n
                msq /= np

                if msq < min_msq or min_msq < 0:
                    phys_var_best = phys_var.copy()
                    min_msq = msq

                print('cda: ', cda, ' crr: ', crr, ' wind_v: ', wind_v, ' wind_dir: ', wind_dir, ' rmsq: ', sqrt(msq))


# Compute various power averages
avg_comp_pow_segs = 0.
avg_data_pow_segs = 0.
tstamps = []
cpow_pdata = []
dpow_pdata = []
avg_cpow_pdata = []
avg_dpow_pdata = []
for data_seg in data_segments:
    comp_pow_seg = calc_power_data_C(lib_power, data_seg, phys_var_best, use_zero_slope, True)
#    comp_pow_seg = calc_power_data(data_seg, phys_var_best, use_zero_slope, True, 2)
    mean_comp_pow = mean(comp_pow_seg)
    mean_data_pow = mean(data_seg['power'])
    avg_comp_pow_segs += mean_comp_pow
    avg_data_pow_segs += mean_data_pow
    for it, t in enumerate(data_seg['timestamp']):
        tstamps.append(t)
        cpow_pdata.append(comp_pow_seg[it])
        dpow_pdata.append(data_seg['power'][it])
        avg_cpow_pdata.append(mean_comp_pow)
        avg_dpow_pdata.append(mean_data_pow)
avg_comp_pow_segs /= len(data_segments)
avg_data_pow_segs /= len(data_segments)
comp_pow_full = calc_power_data_C(lib_power, data, phys_var_best, use_zero_slope, True)
avg_comp_pow_full = mean(comp_pow_full)

figure()
plot(tstamps, avg_cpow_pdata, 'o')
plot(tstamps, avg_dpow_pdata, 's')
legend(['cpow', 'dpow'])

figure()
plot(tstamps, cpow_pdata, 'o')
plot(tstamps, dpow_pdata, 's')
legend(['cpow', 'dpow'])


# Report

print('Weather Data:')
print(weather_data)
print('Computed Air Rho: ', rho_calc)

print('Optimization Results:')
print('cda:      ', phys_var_best['cda'])
print('crr:      ', phys_var_best['crr'])
print('wind_v:   ', phys_var_best['wind_v'])
print('wind_dir: ', phys_var_best['wind_dir'])
print()
print('Min RMSQ: ', sqrt(min_msq))

print('Calculated segment average power: ', avg_comp_pow_segs)
print('Measured segment average power: ', avg_data_pow_segs)
print('Calculated total average power: ', avg_comp_pow_full)
print('Measured total average power: ', mean(data['power']))

win_len = 60
data_smooth = []
comp_smooth = []
it = 0
while it < len(comp_pow_full) - win_len + 1:
    win_dat = data['power'][it : it + win_len]
    win_comp = comp_pow_full[it : it + win_len]

    avg_dat = mean(win_dat)
    avg_comp = mean(win_comp)

    data_smooth.append(avg_dat)
    comp_smooth.append(avg_comp)

    it += 1

figure()
plot(data['power'], 'x')
plot(comp_pow_full, '+')

figure()
plot(data_smooth)
plot(comp_smooth)

show()
