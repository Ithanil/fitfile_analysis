import sys
from pylab import *

from calc.calc_speed import calc_speed_static
from parse.get_weather_data import get_weather_data
from calc.calc_rho import calc_rho_humid

verbosity = 0


# get weather
#weather_data = get_weather_data(data)
#rho_calc = calc_rho_humid(weather_data.temp[0], weather_data.pres[0], weather_data.rhum[0])
#print('Weather Data:')
#print(weather_data)
#print('Computed Air Rho: ', rho_calc)

g = 9.81
rho = 1.225
wind_v = 0.
wind_dir = 0.

slope = 0.
dir = 0.

phys_var_1 = {
    'mass'       : 72+10,
    'crr'        : 0.0043,
    'cda'        : 0.28,
    'loss'       : 0.03,
    'g'          : g,
    'rho'        : rho,
    'wind_v'     : wind_v,
    'wind_dir'   : wind_dir
}

phys_var_2 = {
    'mass'       : 72+10,
    'crr'        : 0.009,
    'cda'        : 0.28,
    'loss'       : 0.03,
    'g'          : g,
    'rho'        : rho,
    'wind_v'     : wind_v,
    'wind_dir'   : wind_dir
}

comp_pows = linspace(50., 450., 40, True)
comp_v1 = []
for pow in comp_pows:
    comp_v1.append(3.6*calc_speed_static(pow, 0., 0., phys_var_1, False))

comp_v2 = []
for pow in comp_pows:
    comp_v2.append(3.6*calc_speed_static(pow, 0., 0., phys_var_2, False))

comp_vdiff = []
for it in range(len(comp_pows)):
    comp_vdiff.append(comp_v2[it] - comp_v1[it])

figure()
plot(comp_pows, comp_v1)
plot(comp_pows, comp_v2)
legend(['1', '2'])

figure()
plot(comp_pows, comp_vdiff)

show()
