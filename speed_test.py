import sys
from pylab import *

from calc.calc_speed import calc_speed_static
from calc.calc_power import calc_power
from parse.get_weather_data import get_weather_data
from calc.calc_rho import calc_rho_humid, calc_rho_dry

verbosity = 0


# get weather
#weather_data = get_weather_data(data)
#rho_calc_1 = calc_rho_humid(20, 1013, 50)
#rho_calc_2 = calc_rho_humid(3, 1013, 50)
rho_calc_1 = calc_rho_dry(30, 1013)
rho_calc_2 = calc_rho_dry(0, 1013)
print('Computed Warm Rho: ', rho_calc_1)
print('Computer Cold Rho: ', rho_calc_2)

g = 9.81
wind_v = 0.
wind_dir = 0.

slope = 0. # only positive slopes will work atm!!!
dir = 0.

phys_var_1 = {
    'mass'       : 70+10,
    'rot_mass'   : 0.15 * 4.*pi**2 / 2.105**2,
    'crr'        : 0.0045,
    'cda'        : 0.2,
    'loss'       : 0.03,
    'g'          : g,
    'rho'        : rho_calc_1,
    'wind_v'     : wind_v,
    'wind_dir'   : wind_dir
}

phys_var_2 = {
    'mass'       : 70+10,
    'rot_mass'   : 0.15 * 4.*pi**2 / 2.105**2,
    'crr'        : 0.0045,
    'cda'        : 0.2,
    'loss'       : 0.03,
    'g'          : g,
    'rho'        : rho_calc_2,
    'wind_v'     : wind_v,
    'wind_dir'   : wind_dir
}

comp_pows = linspace(50., 450., 40, True)
calc_pows_v1 = []
calc_pows_v2 = []
comp_v1 = []
comp_v2 = []
for pow in comp_pows:
    v1 = calc_speed_static(pow, dir, slope, phys_var_1, False)
    v2 = calc_speed_static(pow, dir, slope, phys_var_2, False)
    calc_pows_v1.append(calc_power(v1, v1, 1., dir, slope, phys_var_1, False))
    calc_pows_v2.append(calc_power(v2, v2, 1., dir, slope, phys_var_2, False))
    comp_v1.append(3.6*v1)
    comp_v2.append(3.6*v2)

comp_vdiff = []
for it in range(len(comp_pows)):
    comp_vdiff.append(comp_v2[it] - comp_v1[it])

figure()
plot(comp_pows, comp_v1)
plot(comp_pows, comp_v2)
legend(['1', '2'])

figure()
plot(comp_pows, comp_vdiff)


# diagnostic plot/printout
#figure()
#plot(comp_pows, calc_pows_v1)
#plot(comp_pows, calc_pows_v2)
#print(calc_pows_v1)
#print(calc_pows_v2)


pow_dirtest = 200.
dir_delta = 5.
n_dir = int(360./dir_delta) + 1
dirs = linspace(0., 360., n_dir, True)
phys_var_1['wind_v'] = 0.
v_nowind = 3.6*calc_speed_static(pow_dirtest, 0., 0., phys_var_1, False)
phys_var_1['wind_v'] = 3.
phys_var_1['wind_dir'] = 90.

v_dirs = []
for dir in dirs:
    v_dirs.append(3.6*calc_speed_static(pow_dirtest, dir, 0., phys_var_1, False))

figure()
plot(dirs, v_dirs)
plot([0,360.],[v_nowind, v_nowind])

show()
